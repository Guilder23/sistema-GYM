from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.contrib.auth.models import User
from .models import Product, Sale, ProductCategory, SaleItem, ProductStockHistory
from apps.clients.models import Client
from apps.core.models import UserProfile
from apps.core.permissions import role_required, get_user_role, get_linked_client


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def product_list(request):
    search_query = request.GET.get('q', '')
    products = Product.objects.all().order_by('name')
    if search_query:
        products = products.filter(name__icontains=search_query)
    context = {'products': products, 'search_query': search_query}
    return render(request, 'inventory/product_list.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def product_create(request):
    categories = ProductCategory.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        price = request.POST.get('price', 0)
        # Ignoramos stock del POST para que sea 0 por defecto al crear
        min_stock = request.POST.get('min_stock', 5)
        category_id = request.POST.get('category_id')
        barcode = request.POST.get('barcode', '')
        
        category = None
        if category_id:
            category = ProductCategory.objects.get(id=category_id)
            
        Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=0, # Siempre 0 al crear
            min_stock=min_stock,
            category=category,
            barcode=barcode or None
        )
        messages.success(request, 'Producto creado con stock inicial en cero. Usa Ajuste de Stock para agregar cantidad.')
        return redirect('product_list')
    
    return render(request, 'inventory/product_form.html', {'categories': categories})


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def product_stock_adjust(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        adjustment_type = request.POST.get('adjustment_type')
        amount = int(request.POST.get('amount', 0))
        reason = request.POST.get('reason', '')

        if amount <= 0:
            messages.error(request, 'La cantidad debe ser mayor a cero.')
            return redirect('product_stock_adjust', product_id=product.id)

        with transaction.atomic():
            if adjustment_type == 'ENTRY':
                product.stock += amount
                change = amount
            else:
                if product.stock < amount:
                    messages.error(request, 'No hay suficiente stock para reducir esa cantidad.')
                    return redirect('product_stock_adjust', product_id=product.id)
                product.stock -= amount
                change = -amount
            
            product.save()
            
            ProductStockHistory.objects.create(
                product=product,
                change_amount=change,
                current_stock=product.stock,
                adjustment_type=adjustment_type,
                reason=reason,
                created_by=request.user
            )
            
        messages.success(request, f'Stock actualizado correctamente. Nuevo stock: {product.stock}')
        return redirect('product_list')

    history = product.stock_history.all().order_by('-created_at')
    return render(request, 'inventory/product_stock_adjust.html', {'product': product, 'history': history})


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = ProductCategory.objects.all()
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description', '')
        product.price = request.POST.get('price', 0)
        product.stock = request.POST.get('stock', 0)
        product.min_stock = request.POST.get('min_stock', 5)
        category_id = request.POST.get('category_id')
        product.barcode = request.POST.get('barcode', '') or None
        
        if category_id:
            product.category = ProductCategory.objects.get(id=category_id)
        else:
            product.category = None
            
        product.save()
        messages.success(request, 'Producto actualizado correctamente.')
        return redirect('product_list')
    
    return render(request, 'inventory/product_form.html', {'product': product, 'categories': categories})


# Lógica del Carrito de Compras
@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_add(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    
    if product.stock <= 0:
        messages.error(request, f'El producto {product.name} está agotado.')
        return redirect('product_list')
        
    p_id = str(product_id)
    if p_id in cart:
        cart[p_id]['quantity'] += 1
    else:
        cart[p_id] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1
        }
    
    request.session['cart'] = cart
    messages.success(request, f'{product.name} añadido al carrito.')
    return redirect('product_list')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_detail(request):
    cart = request.session.get('cart', {})
    clients = Client.objects.filter(is_active=True).order_by('first_name')
    # También obtener usuarios del sistema para venderles
    staff_users = User.objects.filter(is_active=True, profile__role__in=[
        UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION, UserProfile.ROLE_TRAINER
    ]).order_by('username')
    
    total = 0
    cart_items = []
    
    for p_id, item in cart.items():
        subtotal = float(item['price']) * item['quantity']
        total += subtotal
        cart_items.append({
            'id': p_id,
            'name': item['name'],
            'price': item['price'],
            'quantity': item['quantity'],
            'subtotal': subtotal
        })
        
    context = {
        'cart_items': cart_items,
        'total': total,
        'clients': clients,
        'staff_users': staff_users
    }
    return render(request, 'inventory/cart_detail.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_remove(request, product_id):
    cart = request.session.get('cart', {})
    p_id = str(product_id)
    if p_id in cart:
        del cart[p_id]
        request.session['cart'] = cart
        messages.success(request, 'Producto eliminado del carrito.')
    return redirect('cart_detail')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_clear(request):
    request.session['cart'] = {}
    return redirect('product_list')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def cart_checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('product_list')
        
    if request.method == 'POST':
        buyer_type = request.POST.get('buyer_type') # 'client' or 'staff'
        client_id = request.POST.get('client_id')
        staff_id = request.POST.get('staff_id')
        notes = request.POST.get('notes', '')
        
        client = None
        user = None
        
        if buyer_type == 'client' and client_id:
            client = get_object_or_404(Client, id=client_id)
        elif buyer_type == 'staff' and staff_id:
            user = get_object_or_404(User, id=staff_id)
            
        total = sum(float(item['price']) * item['quantity'] for item in cart.values())
        
        with transaction.atomic():
            sale = Sale.objects.create(
                client=client,
                user=user,
                total=total,
                notes=notes
            )
            
            for p_id, item in cart.items():
                product = get_object_or_404(Product, id=p_id)
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )
                # Descontar stock
                product.stock -= item['quantity']
                product.save()
            
        request.session['cart'] = {}
        messages.success(request, 'Venta realizada con éxito.')
        return redirect('sale_list')
        
    return redirect('cart_detail')


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION, UserProfile.ROLE_TRAINER, UserProfile.ROLE_CLIENT)
def my_purchases(request):
    role = get_user_role(request.user)
    if role == UserProfile.ROLE_CLIENT:
        client = get_linked_client(request.user)
        purchases = Sale.objects.filter(client=client).order_by('-date')
    else:
        # Para Admin, Recep, Entrenador
        purchases = Sale.objects.filter(user=request.user).order_by('-date')
    
    context = {'purchases': purchases}
    return render(request, 'inventory/my_purchases.html', context)


@role_required(UserProfile.ROLE_ADMIN, UserProfile.ROLE_RECEPTION)
def sale_list(request):
    sales = Sale.objects.all().order_by('-date')
    context = {'sales': sales}
    return render(request, 'inventory/sale_list.html', context)
