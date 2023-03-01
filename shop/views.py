from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from meta.views import Meta
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from .filters import ItemFIlters
from .models import Item, Category, OrderItem, Order, Coupon
from .forms import CheckoutForm, CouponForm
from users.models import Address
from django.views.decorators.csrf import csrf_exempt
import stripe

from .utils import random_string_generator

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):  # pragma: no cover
    payload = request.body.decode('utf-8')
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload'
        print(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        print(e)
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        user = User.objects.get(id=session.get('metadata').get('user_id'))
        order = Order.objects.get(user=user, ordered=False)
        order_items = order.items.all()
        order_items.update(ordered=True)
        for item in order_items:
            item.save()

        order.ordered = True
        order.ref_code = random_string_generator(5)
        order.save()

    return HttpResponse(status=200)


def get_or_create_stripe_customer(request):  # pragma: no cover
    if request.user.profile.stripe_customer_id is None:
        stripe_customer = stripe.Customer.create(
            email=request.user.email,
            name=request.user.username,
            phone=request.user.profile.phone_no
        )
        request.user.profile.stripe_customer_id = stripe_customer.id
        request.user.profile.save()
        return stripe_customer.id
    else:
        return request.user.profile.stripe_customer_id


class ItemDetailView(DetailView):
    model = Item
    template_name = "shop/item_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data()
        context['meta'] = self.get_object().as_meta(self.request)
        return context

    def get_queryset(self, **kwargs):
        return Item.objects.filter(slug=self.kwargs.get('slug'))


def category_items(request, slug):
    category = get_object_or_404(Category, slug=slug)
    meta = category.as_meta(request)

    queryset = category.items.all()

    filtered_items = ItemFIlters(request.GET, queryset)
    filtered_items_form = filtered_items.form

    filtered_items_qs = filtered_items.qs
    paginator = Paginator(filtered_items_qs, 9)

    page = request.GET.get('page')
    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)

    context = {
        "category": category,
        'response': response,
        'filtered_qs_form': filtered_items_form,
        "meta": meta
    }
    return render(request, 'shop/category_items.html', context)


@login_required
def add_to_cart(request, slug):  # pragma: no cover
    item = get_object_or_404(Item, slug=slug)
    if item.quantity < 1:
        messages.warning(request, _("This item is out of stock."))
        #  ? Redirect to Cart
        return redirect("cart")

    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False,
    )
    added_item_qty = Item.objects.filter(slug=slug).first()
    added_item_qty.quantity -= 1
    added_item_qty.save()
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.success(request, _("This item quantity was updated."))
            return redirect("cart")
        else:
            order.items.add(order_item)
            messages.success(request, _("This item was added to your cart."))
            return redirect("cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.success(request, _("This item was added to your cart."))
        return redirect("cart")


@login_required
def remove_from_cart(request, slug):  # pragma: no cover
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    item.quantity += Order.objects.filter(
        user=request.user,
        ordered=False,
    ).first().items.filter(item__slug=slug).first().quantity

    item.save()
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.warning(request, _(
                "This item was removed from your cart."))
            return redirect("cart")
        else:
            messages.warning(request, _("This item was not in your cart"))
            return redirect("cart", slug=slug)
    else:
        messages.warning(request, _("You do not have an active order"))
        return redirect("cart", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):  # pragma: no cover
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    item.quantity += 1
    item.save()
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.success(request, _("This item quantity was updated."))
            return redirect("cart")
        else:
            messages.warning(request, _("This item was not in your cart"))
            return redirect("cart", slug=slug)
    else:
        messages.warning(request, _("You do not have an active order"))
        return redirect("cart", slug=slug)


@login_required
def cart(request):  # pragma: no cover
    meta = Meta(
        title=_("Cart"),
        description=settings.CONFIG.get('description'),
    )
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        context = {
            'order': order,
            'meta': meta,
            'coupon_form': CouponForm()
        }
        return render(request, 'shop/cart.html', context)
    except ObjectDoesNotExist:
        context = {
            'meta': meta
        }
        return render(request, "shop/cart.html", context)


@login_required
def checkout(request):  # pragma: no cover
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        if request.method == "POST":
            form = CheckoutForm(request.POST, request.FILES)
            if form.is_valid():
                address = Address.objects.create(
                    street_address=form.cleaned_data.get('street_address'),
                    postal_code=form.cleaned_data.get('postal_code'),
                    city=form.cleaned_data.get('city'),
                    user=request.user
                )
                order.delivery_address = address
                order.save()
                # payment_method = form.cleaned_data.get('payment_method')
                data = []
                for order_item in order.items.all():
                    data.append(
                        {
                            'quantity': order_item.quantity,
                            'currency': 'usd',
                            'amount': order_item.item.discount_price * 100 if order_item.item.discount_price else order_item.item.price * 100,
                            'name': order_item.item.name,
                        }
                    )
                try:
                    checkout_session = stripe.checkout.Session.create(
                        line_items=data,
                        payment_method_types=[
                            'card'
                        ],
                        customer=get_or_create_stripe_customer(request),
                        mode='payment',
                        success_url=request.build_absolute_uri(
                            reverse('payment_successful')),
                        metadata={
                            "user_id": request.user.id,
                        },
                        cancel_url=request.build_absolute_uri(
                            reverse('checkout')),

                    )
                    return redirect(checkout_session.url)
                except Exception as e:
                    messages.warning(request, e)
                    return redirect('checkout')

        form = CheckoutForm()
        context = {
            "form": form,
            "order": order,
            "meta": Meta(
                title=_("Checkout"),
                description=settings.CONFIG.get('description'),
            )
        }

        return render(request, 'shop/checkout.html', context)
    except ObjectDoesNotExist:
        messages.warning(request, _("You do not have an active order"))
        return redirect('index')


@login_required
def add_coupon(request):  # pragma: no cover
    try:
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=request.user, ordered=False)
                try:
                    coupon = Coupon.objects.get(code=code)
                except ObjectDoesNotExist:
                    messages.warning(request, _("This coupon does not exist."))
                    return redirect("cart")

                if not coupon.is_expired:
                    order.coupon = coupon
                    order.save()
                    messages.success(request, _("Coupon Added Successfully."))
                    return redirect("cart")
                else:
                    messages.warning(request, _("Coupon is expired."))
                    return redirect("cart")

            except ObjectDoesNotExist:
                messages.warning(request, _("You do not have an active order"))
                return redirect("cart")
    except Exception as ex:
        print(ex)
        return redirect("cart")


@login_required
def remove_coupon(request):  # pragma: no cover
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        order.coupon = None
        order.save()
        messages.success(request, _("Coupon Removed Successfully."))
        return redirect("cart")
    except ObjectDoesNotExist:
        messages.warning(request, _("Error Occured"))
        return redirect("cart")


def payment_successful(request):  # pragma: no cover
    return render(request, 'shop/payment_successful.html', {
        "meta": Meta(title=_("Payment Successful"))
    })


@login_required
def user_orders(request):  # pragma: no cover
    return render(request, 'shop/user_orders.html', {
        "meta": Meta(
            title="My Orders",
            description=_(
                '''Give us a call or drop by anytime, we endeavour to answer all enquiries within 24 hours on
                business days. We will be happy to answer your questions.'''
            )
        ),
        'orders': Order.objects.filter(user=request.user, ordered=True)
    })
