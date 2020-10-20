from django.shortcuts import render, get_object_or_404, redirect, HttpResponseRedirect, reverse
from django.contrib import messages
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, Order, OrderItem, CheckoutDetail, Payment
from .forms import CheckoutDetailsForm
from django.views.generic import ListView, DetailView, View
from django.utils import timezone

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class Home_page_view(ListView):
    model = Item
    paginate_by = 8
    template_name = 'FirstWebApp/home-page.html'

def Search_view(request):
    all_items = Item.objects.all()
    query = request.GET.get("q")
    if query:
        all_items = all_items.filter(Q(category__icontains=query) |
                                     Q(title__icontains=query)
                                     )
    context = {
            'object_list': all_items

        }
    return render(request, 'FirstWebApp/search.html', context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                "object": order
            }
            return render(self.request, 'FirstWebApp/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order.")
            return redirect("/")

@login_required
def checkout_view(request):
    form = CheckoutDetailsForm(request.POST or None)
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        if request.method == 'POST':
            if form.is_valid:
                checkout_form = form.save(commit=False)
                checkout_form.user = request.user
                checkout_form.save()
                order.checkoutdetails = checkout_form
                order.save()
                return redirect('ecommerce:payment')

        context = {
            'form': form
        }
        return render(request, 'FirstWebApp/checkout-page.html', context)
    except ObjectDoesNotExist:
        messages.warning(request, "You do not have an active order.")
        return redirect("/")

class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'FirstWebApp/payment.html', context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="pkr",
                source=token,
                description="My First Test Charge (created for API docs)",
            )
            # creating the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            # assigning the payment to the order
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, 'Order was successful.')
            return redirect('/')

        except stripe.error.CardError as e:
            messages.warning(self.request, f"{e.error.message}")
            return redirect('/')

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, 'Rate Limit error')
            return redirect('/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, 'Invalid parameters')
            return redirect('/')

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, 'Authentication error')
            return redirect('/')

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, 'Network error')
            return redirect('/')

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(self.request, 'Something went wrong, You were not charged')
            return redirect('/')

        except Exception as e:
            # send email to ourselves
            messages.warning(self.request, 'A serious error occured. We have been notified.')
            return redirect('/')

class ProductDetails_view(DetailView):
    model = Item
    template_name = "FirstWebApp/product-page.html"

@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item,
                                                 user=request.user,
                                                 ordered=False
    )
    order_item.save()
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        #checking if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, "The item quantity was updated.")
            return redirect('ecommerce:order-summary')
        else:
            messages.success(request, "This item was added to your cart.")
            order.items.add(order_item)
            return redirect('ecommerce:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user,
                                     ordered_date=ordered_date,

                                     )
        order.items.add(order_item)
        messages.success(request, "This item was added to your cart.")
    return redirect('ecommerce:order-summary')

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # checking if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False,
                )[0]
            order.items.remove(order_item)
            messages.success(request, "This item was removed from your cart.")
            return redirect('ecommerce:order-summary')
        else:
            messages.success(request, "This item was not in your cart.")
            return redirect('ecommerce:product', slug=slug)
    else:
        messages.success(request, "You don't have an active order.")
        return redirect('ecommerce:product', slug=slug)


def remove_single_item_from_cart(request, slug):
        item = get_object_or_404(Item, slug=slug)
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # checking if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=item,
                    user=request.user,
                    ordered=False,
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                return redirect('ecommerce:order-summary')
            else:
                messages.success(request, "This item was not in your cart.")
                return redirect('ecommerce:product', slug=slug)
        else:
            messages.success(request, "You don't have an active order.")
            return redirect('ecommerce:product', slug=slug)

