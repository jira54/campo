# Walk-In Customer Management Design for Resort Operations

## Overview

**Complete Resort Operations Management**
Resorts serve multiple customer types beyond room guests:
- **Restaurant customers** - dining, events, casual dining
- **Bar patrons** - drinks, entertainment, social gatherings  
- **Space bookings** - meetings, events, conferences, weddings
- **Day visitors** - pool, spa, facilities usage
- **Walk-in services** - various on-demand services

---

## 1. Enhanced Sidebar Navigation

### **Updated Structure for Complete Resort Operations**
```html
<nav class="resort-sidebar">
    <div class="sidebar-header">
        <div class="resort-logo">{{ user.business_name|first|upper }}</div>
        <div class="user-info-mini">
            <span class="user-name">{{ user.owner_name }}</span>
            <span class="user-role">{{ user.get_role_display }}</span>
        </div>
    </div>
    
    <div class="sidebar-nav">
        <!-- Main Navigation -->
        <div class="nav-section">
            <div class="nav-section-title">Main</div>
            <a href="{% url 'resort_portal:overview' %}" class="nav-item active">
                <span class="nav-icon">?</span>
                <span class="nav-text">Overview</span>
            </a>
        </div>
        
        <!-- Guest Operations -->
        <div class="nav-section">
            <div class="nav-section-title">Guest Operations</div>
            <a href="{% url 'resort_portal:guests' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Room Guests</span>
            </a>
            <a href="{% url 'resort_portal:rooms' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Rooms</span>
            </a>
        </div>
        
        <!-- Customer Operations -->
        <div class="nav-section">
            <div class="nav-section-title">Customer Operations</div>
            <a href="{% url 'resort_portal:restaurant' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Restaurant</span>
            </a>
            <a href="{% url 'resort_portal:bar' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Bar</span>
            </a>
            <a href="{% url 'resort_portal:events' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Events & Spaces</span>
            </a>
            <a href="{% url 'resort_portal:day_visitors' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Day Visitors</span>
            </a>
        </div>
        
        <!-- Services (Combined) -->
        <div class="nav-section">
            <div class="nav-section-title">Services</div>
            <a href="{% url 'resort_portal:services' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">All Services</span>
            </a>
        </div>
        
        <!-- Reports (Manager Only) -->
        {% if user.can_view_reports %}
        <div class="nav-section">
            <div class="nav-section-title">Reports</div>
            <a href="{% url 'resort_portal:reports' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Reports</span>
            </a>
        </div>
        {% endif %}
        
        <!-- Settings -->
        <div class="nav-section">
            <div class="nav-section-title">Settings</div>
            <a href="{% url 'resort_portal:settings' %}" class="nav-item">
                <span class="nav-icon">?</span>
                <span class="nav-text">Settings</span>
            </a>
        </div>
    </div>
</nav>
```

---

## 2. Restaurant Section Page (/resort/restaurant/)

### **Restaurant Operations Management**
```html
{% extends 'base.html' %}
{% block title %}Restaurant - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Restaurant</h1>
            <div class="header-actions">
                <div class="quick-stats">
                    <div class="stat-item">
                        <span class="number">{{ active_tables }}</span>
                        <span class="label">Active Tables</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">{{ covers_today }}</span>
                        <span class="label">Covers Today</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">KES {{ restaurant_revenue }}</span>
                        <span class="label">Revenue Today</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Internal Navigation Tabs -->
        <div class="section-tabs">
            <button class="tab-btn active" onclick="showTab('table-management')">
                <span class="icon">?</span>
                <span>Table Management</span>
            </button>
            <button class="tab-btn" onclick="showTab('walk-in-seating')">
                <span class="icon">?</span>
                <span>Walk-in Seating</span>
            </button>
            <button class="tab-btn" onclick="showTab('reservations')">
                <span class="icon">?</span>
                <span>Reservations</span>
            </button>
            <button class="tab-btn" onclick="showTab('orders')">
                <span class="icon">?</span>
                <span>Orders</span>
            </button>
            <button class="tab-btn" onclick="showTab('restaurant-analytics')">
                <span class="icon">?</span>
                <span>Analytics</span>
            </button>
        </div>
        
        <!-- Tab Content Areas -->
        <div class="tab-content">
            <!-- Table Management Tab -->
            <div id="table-management" class="tab-pane active">
                <div class="function-content">
                    <div class="restaurant-layout">
                        <div class="layout-controls">
                            <div class="filter-buttons">
                                <button class="filter-btn active" onclick="filterTables('all')">All Tables</button>
                                <button class="filter-btn" onclick="filterTables('available')">Available</button>
                                <button class="filter-btn" onclick="filterTables('occupied')">Occupied</button>
                                <button class="filter-btn" onclick="filterTables('reserved')">Reserved</button>
                            </div>
                            <div class="layout-actions">
                                <button onclick="openAddTableModal()" class="action-btn-small">Add Table</button>
                                <button onclick="changeLayoutView()" class="action-btn-small">Change View</button>
                            </div>
                        </div>
                        
                        <div class="tables-grid">
                            {% for table in restaurant_tables %}
                            <div class="table-card status-{{ table.status }}" onclick="manageTable('{{ table.id }}')">
                                <div class="table-header">
                                    <div class="table-number">Table {{ table.table_number }}</div>
                                    <div class="table-capacity">{{ table.capacity }} seats</div>
                                </div>
                                
                                <div class="table-info">
                                    {% if table.current_customer %}
                                    <div class="customer-info">
                                        <span class="customer-name">{{ table.current_customer.name }}</span>
                                        <span class="party-size">{{ table.current_customer.party_size }} guests</span>
                                        <span class="time-seated">{{ table.time_seated|timeago }}</span>
                                    </div>
                                    {% endif %}
                                    
                                    {% if table.reservation %}
                                    <div class="reservation-info">
                                        <span class="reservation-time">{{ table.reservation.time|time:"H:i" }}</span>
                                        <span class="reservation-name">{{ table.reservation.customer_name }}</span>
                                        <span class="party-size">{{ table.reservation.party_size }} guests</span>
                                    </div>
                                    {% endif %}
                                    
                                    <div class="table-status">{{ table.get_status_display }}</div>
                                </div>
                                
                                <div class="table-actions">
                                    {% if table.status == 'available' %}
                                    <button onclick="seatWalkIn('{{ table.id }}')" class="action-btn-small">Seat Walk-in</button>
                                    {% elif table.status == 'occupied' %}
                                    <button onclick="addOrder('{{ table.id }}')" class="action-btn-small">Add Order</button>
                                    <button onclick="processPayment('{{ table.id }}')" class="action-btn-small">Payment</button>
                                    {% elif table.status == 'reserved' %}
                                    <button onclick="seatReservation('{{ table.id }}')" class="action-btn-small">Seat Guest</button>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Walk-in Seating Tab -->
            <div id="walk-in-seating" class="tab-pane">
                <div class="function-content">
                    <div class="walk-in-queue">
                        <h3>Walk-in Queue</h3>
                        <div class="queue-stats">
                            <div class="stat-item">
                                <span class="number">{{ waiting_count }}</span>
                                <span class="label">Waiting</span>
                            </div>
                            <div class="stat-item">
                                <span class="number">{{ avg_wait_time }}</span>
                                <span class="label">Avg Wait Time</span>
                            </div>
                        </div>
                        
                        <div class="queue-list">
                            {% for customer in walk_in_queue %}
                            <div class="queue-item">
                                <div class="customer-info">
                                    <h4>{{ customer.name }}</h4>
                                    <p class="party-size">{{ customer.party_size }} guests</p>
                                    <p class="wait-time">Waiting for {{ customer.wait_time|timeago }}</p>
                                    <p class="phone">{{ customer.phone }}</p>
                                </div>
                                <div class="customer-actions">
                                    <button onclick="assignTable('{{ customer.id }}')" class="action-btn-small">Assign Table</button>
                                    <button onclick="contactCustomer('{{ customer.id }}')" class="action-btn-small">Contact</button>
                                    <button onclick="removeFromQueue('{{ customer.id }}')" class="action-btn-small remove">Remove</button>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="quick-walk-in">
                        <h3>Quick Walk-in Seating</h3>
                        <form method="POST" class="walk-in-form">
                            {% csrf_token %}
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Customer Name *</label>
                                    <input type="text" name="customer_name" required>
                                </div>
                                <div class="form-group">
                                    <label>Phone Number</label>
                                    <input type="tel" name="phone_number">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Party Size *</label>
                                    <select name="party_size" required>
                                        <option value="">Select size...</option>
                                        {% for size in party_sizes %}
                                        <option value="{{ size }}">{{ size }} guests</option>
                                        {% endfor %}
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Preferred Table Type</label>
                                    <select name="table_type">
                                        <option value="any">Any</option>
                                        <option value="booth">Booth</option>
                                        <option value="table">Table</option>
                                        <option value="outdoor">Outdoor</option>
                                        <option value="private">Private</option>
                                    </select>
                                </div>
                            </div>
                            <button type="submit" class="submit-btn">Add to Queue</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <!-- Reservations Tab -->
            <div id="reservations" class="tab-pane">
                <div class="function-content">
                    <div class="reservation-controls">
                        <div class="date-picker">
                            <input type="date" id="reservation-date" value="{{ today|date:'Y-m-d' }}">
                            <button onclick="loadReservations()" class="action-btn-small">Load</button>
                        </div>
                        <div class="filter-buttons">
                            <button class="filter-btn active" onclick="filterReservations('all')">All</button>
                            <button class="filter-btn" onclick="filterReservations('today')">Today</button>
                            <button class="filter-btn" onclick="filterReservations('upcoming')">Upcoming</button>
                            <button class="filter-btn" onclick="filterReservations('cancelled')">Cancelled</button>
                        </div>
                        <button onclick="openAddReservationModal()" class="action-btn-small">Add Reservation</button>
                    </div>
                    
                    <div class="reservations-timeline">
                        {% for reservation in reservations %}
                        <div class="reservation-item status-{{ reservation.status }}">
                            <div class="reservation-time">
                                <span class="time">{{ reservation.time|time:"H:i" }}</span>
                                <span class="duration">{{ reservation.duration }}h</span>
                            </div>
                            <div class="reservation-details">
                                <h4>{{ reservation.customer_name }}</h4>
                                <p class="party-size">{{ reservation.party_size }} guests</p>
                                <p class="table">Table {{ reservation.table.table_number }}</p>
                                <p class="phone">{{ reservation.phone }}</p>
                                {% if reservation.notes %}
                                <p class="notes">{{ reservation.notes }}</p>
                                {% endif %}
                            </div>
                            <div class="reservation-actions">
                                {% if reservation.status == 'confirmed' %}
                                <button onclick="confirmArrival('{{ reservation.id }}')" class="action-btn-small">Arrived</button>
                                <button onclick="modifyReservation('{{ reservation.id }}')" class="action-btn-small">Modify</button>
                                <button onclick="cancelReservation('{{ reservation.id }}')" class="action-btn-small cancel">Cancel</button>
                                {% elif reservation.status == 'arrived' %}
                                <button onclick="assignTable('{{ reservation.id }}')" class="action-btn-small">Assign Table</button>
                                {% elif reservation.status == 'cancelled' %}
                                <button onclick="reactivateReservation('{{ reservation.id }}')" class="action-btn-small">Reactivate</button>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <!-- Orders Tab -->
            <div id="orders" class="tab-pane">
                <div class="function-content">
                    <div class="orders-controls">
                        <div class="filter-buttons">
                            <button class="filter-btn active" onclick="filterOrders('active')">Active</button>
                            <button class="filter-btn" onclick="filterOrders('pending')">Pending</button>
                            <button class="filter-btn" onclick="filterOrders('completed')">Completed</button>
                            <button class="filter-btn" onclick="filterOrders('cancelled')">Cancelled</button>
                        </div>
                        <button onclick="openAddOrderModal()" class="action-btn-small">Add Order</button>
                    </div>
                    
                    <div class="orders-grid">
                        {% for order in orders %}
                        <div class="order-card status-{{ order.status }}">
                            <div class="order-header">
                                <div class="order-info">
                                    <span class="order-number">#{{ order.order_number }}</span>
                                    <span class="table">Table {{ order.table.table_number }}</span>
                                    <span class="customer">{{ order.customer.name }}</span>
                                </div>
                                <div class="order-time">
                                    <span class="time">{{ order.created_at|time:"H:i" }}</span>
                                    <span class="status">{{ order.get_status_display }}</span>
                                </div>
                            </div>
                            
                            <div class="order-items">
                                {% for item in order.items %}
                                <div class="order-item">
                                    <span class="quantity">{{ item.quantity }}x</span>
                                    <span class="item-name">{{ item.menu_item.name }}</span>
                                    <span class="price">KES {{ item.price }}</span>
                                </div>
                                {% endfor %}
                            </div>
                            
                            <div class="order-totals">
                                <div class="subtotal">
                                    <span class="label">Subtotal:</span>
                                    <span class="value">KES {{ order.subtotal }}</span>
                                </div>
                                <div class="tax">
                                    <span class="label">Tax:</span>
                                    <span class="value">KES {{ order.tax }}</span>
                                </div>
                                <div class="total">
                                    <span class="label">Total:</span>
                                    <span class="value">KES {{ order.total }}</span>
                                </div>
                            </div>
                            
                            <div class="order-actions">
                                {% if order.status == 'pending' %}
                                <button onclick="confirmOrder('{{ order.id }}')" class="action-btn-small">Confirm</button>
                                <button onclick="modifyOrder('{{ order.id }}')" class="action-btn-small">Modify</button>
                                {% elif order.status == 'confirmed' %}
                                <button onclick="markReady('{{ order.id }}')" class="action-btn-small">Mark Ready</button>
                                <button onclick="addItem('{{ order.id }}')" class="action-btn-small">Add Item</button>
                                {% elif order.status == 'ready' %}
                                <button onclick="completeOrder('{{ order.id }}')" class="action-btn-small">Complete</button>
                                {% endif %}
                                <button onclick="processPayment('{{ order.id }}')" class="action-btn-small">Payment</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <!-- Restaurant Analytics Tab -->
            <div id="restaurant-analytics" class="tab-pane">
                <div class="function-content">
                    <div class="analytics-dashboard">
                        <div class="period-selector">
                            <select id="analytics-period" onchange="updateAnalytics()">
                                <option value="today">Today</option>
                                <option value="week">This Week</option>
                                <option value="month">This Month</option>
                                <option value="quarter">This Quarter</option>
                            </select>
                        </div>
                        
                        <div class="analytics-grid">
                            <div class="analytics-card">
                                <h3>Revenue Performance</h3>
                                <canvas id="revenueChart"></canvas>
                            </div>
                            
                            <div class="analytics-card">
                                <h3>Cover Trends</h3>
                                <canvas id="coversChart"></canvas>
                            </div>
                            
                            <div class="analytics-card">
                                <h3>Table Turnover</h3>
                                <div class="turnover-stats">
                                    {% for table in table_turnover %}
                                    <div class="turnover-item">
                                        <span class="table-number">Table {{ table.table_number }}</span>
                                        <span class="turns">{{ table.turns }} turns</span>
                                        <span class="revenue">KES {{ table.revenue }}</span>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                            
                            <div class="analytics-card">
                                <h3>Popular Items</h3>
                                <div class="popular-items">
                                    {% for item in popular_items %}
                                    <div class="popular-item">
                                        <span class="item-name">{{ item.name }}</span>
                                        <span class="orders">{{ item.orders }} orders</span>
                                        <span class="revenue">KES {{ item.revenue }}</span>
                                    </div>
                                    {% endfor %}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function showTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
}
</script>
{% endblock %}
```

---

## 3. Bar Section Page (/resort/bar/)

### **Bar Operations Management**
```html
{% extends 'base.html' %}
{% block title %}Bar - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Bar</h1>
            <div class="header-actions">
                <div class="quick-stats">
                    <div class="stat-item">
                        <span class="number">{{ active_customers }}</span>
                        <span class="label">Active Customers</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">{{ drinks_served }}</span>
                        <span class="label">Drinks Served</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">KES {{ bar_revenue }}</span>
                        <span class="label">Revenue Today</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Internal Navigation Tabs -->
        <div class="section-tabs">
            <button class="tab-btn active" onclick="showTab('bar-seating')">
                <span class="icon">?</span>
                <span>Bar Seating</span>
            </button>
            <button class="tab-btn" onclick="showTab('drink-orders')">
                <span class="icon">?</span>
                <span>Drink Orders</span>
            </button>
            <button class="tab-btn" onclick="showTab('tab-management')">
                <span class="icon">?</span>
                <span>Tab Management</span>
            </button>
            <button class="tab-btn" onclick="showTab('inventory')">
                <span class="icon">?</span>
                <span>Inventory</span>
            </button>
        </div>
        
        <!-- Tab Content Areas -->
        <div class="tab-content">
            <!-- Bar Seating Tab -->
            <div id="bar-seating" class="tab-pane active">
                <div class="function-content">
                    <div class="bar-layout">
                        <div class="bar-seats">
                            {% for seat in bar_seats %}
                            <div class="seat-card status-{{ seat.status }}" onclick="manageSeat('{{ seat.id }}')">
                                <div class="seat-header">
                                    <div class="seat-number">{{ seat.seat_number }}</div>
                                    <div class="seat-type">{{ seat.get_seat_type_display }}</div>
                                </div>
                                
                                <div class="seat-info">
                                    {% if seat.current_customer %}
                                    <div class="customer-info">
                                        <span class="customer-name">{{ seat.current_customer.name }}</span>
                                        <span class="time-seated">{{ seat.time_seated|timeago }}</span>
                                        <span class="tab-amount">KES {{ seat.current_tab.total }}</span>
                                    </div>
                                    {% endif %}
                                    
                                    <div class="seat-status">{{ seat.get_status_display }}</div>
                                </div>
                                
                                <div class="seat-actions">
                                    {% if seat.status == 'available' %}
                                    <button onclick="seatCustomer('{{ seat.id }}')" class="action-btn-small">Seat Customer</button>
                                    {% elif seat.status == 'occupied' %}
                                    <button onclick="addDrink('{{ seat.id }}')" class="action-btn-small">Add Drink</button>
                                    <button onclick="closeTab('{{ seat.id }}')" class="action-btn-small">Close Tab</button>
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="quick-customer-seating">
                        <h3>Quick Customer Seating</h3>
                        <form method="POST" class="customer-seating-form">
                            {% csrf_token %}
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Customer Name *</label>
                                    <input type="text" name="customer_name" required>
                                </div>
                                <div class="form-group">
                                    <label>Seat Type *</label>
                                    <select name="seat_type" required>
                                        <option value="">Select type...</option>
                                        <option value="bar_stool">Bar Stool</option>
                                        <option value="high_top">High Top</option>
                                        <option value="lounge">Lounge</option>
                                        <option value="outdoor">Outdoor</option>
                                    </select>
                                </div>
                            </div>
                            <button type="submit" class="submit-btn">Seat Customer</button>
                        </form>
                    </div>
                </div>
            </div>
            
            <!-- Drink Orders Tab -->
            <div id="drink-orders" class="tab-pane">
                <div class="function-content">
                    <div class="orders-controls">
                        <div class="filter-buttons">
                            <button class="filter-btn active" onclick="filterOrders('active')">Active</button>
                            <button class="filter-btn" onclick="filterOrders('pending')">Pending</button>
                            <button class="filter-btn" onclick="filterOrders('completed')">Completed</button>
                        </div>
                        <button onclick="openAddDrinkOrderModal()" class="action-btn-small">Add Drink Order</button>
                    </div>
                    
                    <div class="drink-orders-grid">
                        {% for order in drink_orders %}
                        <div class="drink-order-card status-{{ order.status }}">
                            <div class="order-header">
                                <div class="order-info">
                                    <span class="order-number">#{{ order.order_number }}</span>
                                    <span class="seat">Seat {{ order.seat.seat_number }}</span>
                                    <span class="customer">{{ order.customer.name }}</span>
                                </div>
                                <div class="order-time">
                                    <span class="time">{{ order.created_at|time:"H:i" }}</span>
                                    <span class="status">{{ order.get_status_display }}</span>
                                </div>
                            </div>
                            
                            <div class="drink-items">
                                {% for item in order.items %}
                                <div class="drink-item">
                                    <span class="quantity">{{ item.quantity }}x</span>
                                    <span class="drink-name">{{ item.drink.name }}</span>
                                    <span class="price">KES {{ item.price }}</span>
                                </div>
                                {% endfor %}
                            </div>
                            
                            <div class="order-totals">
                                <div class="total">
                                    <span class="label">Total:</span>
                                    <span class="value">KES {{ order.total }}</span>
                                </div>
                            </div>
                            
                            <div class="order-actions">
                                {% if order.status == 'pending' %}
                                <button onclick="confirmOrder('{{ order.id }}')" class="action-btn-small">Confirm</button>
                                {% elif order.status == 'confirmed' %}
                                <button onclick="markReady('{{ order.id }}')" class="action-btn-small">Ready</button>
                                <button onclick="addDrink('{{ order.id }}')" class="action-btn-small">Add Drink</button>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <!-- Tab Management Tab -->
            <div id="tab-management" class="tab-pane">
                <div class="function-content">
                    <div class="active-tabs">
                        <h3>Active Tabs</h3>
                        <div class="tabs-grid">
                            {% for tab in active_tabs %}
                            <div class="tab-card">
                                <div class="tab-header">
                                    <div class="tab-info">
                                        <span class="customer-name">{{ tab.customer.name }}</span>
                                        <span class="seat">Seat {{ tab.seat.seat_number }}</span>
                                        <span class="opened">{{ tab.opened_at|timeago }}</span>
                                    </div>
                                    <div class="tab-total">
                                        <span class="total">KES {{ tab.total }}</span>
                                    </div>
                                </div>
                                
                                <div class="tab-items">
                                    {% for item in tab.items|slice:":5" %}
                                    <div class="tab-item">
                                        <span class="quantity">{{ item.quantity }}x</span>
                                        <span class="drink-name">{{ item.drink.name }}</span>
                                        <span class="price">KES {{ item.price }}</span>
                                    </div>
                                    {% endfor %}
                                    {% if tab.items.count > 5 %}
                                    <div class="more-items">+{{ tab.items.count|add:"-5" }} more items</div>
                                    {% endif %}
                                </div>
                                
                                <div class="tab-actions">
                                    <button onclick="addDrinkToTab('{{ tab.id }}')" class="action-btn-small">Add Drink</button>
                                    <button onclick="viewTabDetails('{{ tab.id }}')" class="action-btn-small">View Details</button>
                                    <button onclick="closeTabPayment('{{ tab.id }}')" class="action-btn-small">Close Tab</button>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="closed-tabs">
                        <h3>Recently Closed Tabs</h3>
                        <div class="closed-tabs-list">
                            {% for tab in closed_tabs %}
                            <div class="closed-tab-item">
                                <div class="tab-info">
                                    <span class="customer-name">{{ tab.customer.name }}</span>
                                    <span class="closed-time">{{ tab.closed_at|timeago }}</span>
                                </div>
                                <div class="tab-total">
                                    <span class="total">KES {{ tab.total }}</span>
                                </div>
                                <div class="tab-actions">
                                    <button onclick="viewClosedTab('{{ tab.id }}')" class="action-btn-small">View</button>
                                    <button onclick="reprintReceipt('{{ tab.id }}')" class="action-btn-small">Reprint</button>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Inventory Tab -->
            <div id="inventory" class="tab-pane">
                <div class="function-content">
                    <div class="inventory-controls">
                        <div class="filter-buttons">
                            <button class="filter-btn active" onclick="filterInventory('all')">All Items</button>
                            <button class="filter-btn" onclick="filterInventory('low')">Low Stock</button>
                            <button class="filter-btn" onclick="filterInventory('out')">Out of Stock</button>
                        </div>
                        <button onclick="openAddInventoryModal()" class="action-btn-small">Add Item</button>
                    </div>
                    
                    <div class="inventory-grid">
                        {% for item in inventory %}
                        <div class="inventory-item stock-{{ item.stock_level }}">
                            <div class="item-header">
                                <div class="item-info">
                                    <span class="item-name">{{ item.drink.name }}</span>
                                    <span class="category">{{ item.drink.category }}</span>
                                </div>
                                <div class="stock-info">
                                    <span class="stock-quantity">{{ item.quantity }}</span>
                                    <span class="unit">{{ item.unit }}</span>
                                </div>
                            </div>
                            
                            <div class="item-details">
                                <div class="detail-item">
                                    <span class="label">Cost per Unit:</span>
                                    <span class="value">KES {{ item.cost_per_unit }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Selling Price:</span>
                                    <span class="value">KES {{ item.selling_price }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Last Restocked:</span>
                                    <span class="value">{{ item.last_restocked|date:"M d, Y" }}</span>
                                </div>
                            </div>
                            
                            <div class="item-actions">
                                <button onclick="updateStock('{{ item.id }}')" class="action-btn-small">Update Stock</button>
                                <button onclick="adjustPrice('{{ item.id }}')" class="action-btn-small">Adjust Price</button>
                                <button onclick="viewHistory('{{ item.id }}')" class="action-btn-small">History</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function showTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
}
</script>
{% endblock %}
```

---

## 4. Events & Spaces Section Page (/resort/events/)

### **Event and Space Booking Management**
```html
{% extends 'base.html' %}
{% block title %}Events & Spaces - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Events & Spaces</h1>
            <div class="header-actions">
                <div class="quick-stats">
                    <div class="stat-item">
                        <span class="number">{{ active_events }}</span>
                        <span class="label">Active Events</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">{{ upcoming_bookings }}</span>
                        <span class="label">Upcoming</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">KES {{ events_revenue }}</span>
                        <span class="label">Revenue Today</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Internal Navigation Tabs -->
        <div class="section-tabs">
            <button class="tab-btn active" onclick="showTab('space-availability')">
                <span class="icon">?</span>
                <span>Space Availability</span>
            </button>
            <button class="tab-btn" onclick="showTab('bookings')">
                <span class="icon">?</span>
                <span>Bookings</span>
            </button>
            <button class="tab-btn" onclick="showTab('event-management')">
                <span class="icon">?</span>
                <span>Event Management</span>
            </button>
            <button class="tab-btn" onclick="showTab('calendar')">
                <span class="icon">?</span>
                <span>Calendar</span>
            </button>
        </div>
        
        <!-- Tab Content Areas -->
        <div class="tab-content">
            <!-- Space Availability Tab -->
            <div id="space-availability" class="tab-pane active">
                <div class="function-content">
                    <div class="availability-controls">
                        <div class="date-picker">
                            <input type="date" id="availability-date" value="{{ today|date:'Y-m-d' }}">
                            <button onclick="loadAvailability()" class="action-btn-small">Load</button>
                        </div>
                        <div class="view-toggle">
                            <button class="view-btn active" onclick="setView('grid')">Grid View</button>
                            <button class="view-btn" onclick="setView('list')">List View</button>
                        </div>
                    </div>
                    
                    <div class="spaces-grid">
                        {% for space in event_spaces %}
                        <div class="space-card availability-{{ space.availability_status }}">
                            <div class="space-header">
                                <div class="space-info">
                                    <h3>{{ space.name }}</h3>
                                    <p class="capacity">{{ space.capacity }} guests</p>
                                    <p class="type">{{ space.get_space_type_display }}</p>
                                </div>
                                <div class="space-status">
                                    <span class="status">{{ space.get_availability_display }}</span>
                                    <span class="rate">KES {{ space.rate_per_hour }}/hour</span>
                                </div>
                            </div>
                            
                            <div class="space-details">
                                <div class="detail-item">
                                    <span class="label">Features:</span>
                                    <span class="value">{{ space.features|join:", " }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Setup Time:</span>
                                    <span class="value">{{ space.setup_time }} hours</span>
                                </div>
                                {% if space.current_booking %}
                                <div class="current-booking">
                                    <span class="label">Current Event:</span>
                                    <span class="value">{{ space.current_booking.event_name }}</span>
                                    <span class="time">{{ space.current_booking.start_time|time:"H:i" }} - {{ space.current_booking.end_time|time:"H:i" }}</span>
                                </div>
                                {% endif %}
                            </div>
                            
                            <div class="space-actions">
                                {% if space.availability_status == 'available' %}
                                <button onclick="quickBook('{{ space.id }}')" class="action-btn-small">Quick Book</button>
                                <button onclick="viewDetails('{{ space.id }}')" class="action-btn-small">View Details</button>
                                {% elif space.availability_status == 'booked' %}
                                <button onclick="viewBooking('{{ space.current_booking.id }}')" class="action-btn-small">View Booking</button>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <!-- Bookings Tab -->
            <div id="bookings" class="tab-pane">
                <div class="function-content">
                    <div class="bookings-controls">
                        <div class="filter-buttons">
                            <button class="filter-btn active" onclick="filterBookings('all')">All</button>
                            <button class="filter-btn" onclick="filterBookings('today')">Today</button>
                            <button class="filter-btn" onclick="filterBookings('upcoming')">Upcoming</button>
                            <button class="filter-btn" onclick="filterBookings('past')">Past</button>
                            <button class="filter-btn" onclick="filterBookings('cancelled')">Cancelled</button>
                        </div>
                        <button onclick="openAddBookingModal()" class="action-btn-small">New Booking</button>
                    </div>
                    
                    <div class="bookings-list">
                        {% for booking in bookings %}
                        <div class="booking-card status-{{ booking.status }}">
                            <div class="booking-header">
                                <div class="booking-info">
                                    <h4>{{ booking.event_name }}</h4>
                                    <p class="organizer">{{ booking.organizer_name }}</p>
                                    <p class="contact">{{ booking.contact_phone }}</p>
                                </div>
                                <div class="booking-dates">
                                    <span class="date">{{ booking.start_date|date:"M d, Y" }}</span>
                                    <span class="time">{{ booking.start_time|time:"H:i" }} - {{ booking.end_time|time:"H:i" }}</span>
                                </div>
                            </div>
                            
                            <div class="booking-details">
                                <div class="space-info">
                                    <span class="label">Space:</span>
                                    <span class="value">{{ booking.space.name }}</span>
                                </div>
                                <div class="guest-info">
                                    <span class="label">Expected Guests:</span>
                                    <span class="value">{{ booking.expected_guests }}</span>
                                </div>
                                <div class="pricing-info">
                                    <span class="label">Total Cost:</span>
                                    <span class="value">KES {{ booking.total_cost }}</span>
                                </div>
                                {% if booking.special_requirements %}
                                <div class="requirements">
                                    <span class="label">Special Requirements:</span>
                                    <span class="value">{{ booking.special_requirements }}</span>
                                </div>
                                {% endif %}
                            </div>
                            
                            <div class="booking-actions">
                                {% if booking.status == 'confirmed' %}
                                <button onclick="checkInEvent('{{ booking.id }}')" class="action-btn-small">Check-in</button>
                                <button onclick="modifyBooking('{{ booking.id }}')" class="action-btn-small">Modify</button>
                                <button onclick="cancelBooking('{{ booking.id }}')" class="action-btn-small cancel">Cancel</button>
                                {% elif booking.status == 'checked_in' %}
                                <button onclick="addServices('{{ booking.id }}')" class="action-btn-small">Add Services</button>
                                <button onclick="checkOutEvent('{{ booking.id }}')" class="action-btn-small">Check-out</button>
                                {% elif booking.status == 'completed' %}
                                <button onclick="viewInvoice('{{ booking.id }}')" class="action-btn-small">Invoice</button>
                                <button onclick="feedback('{{ booking.id }}')" class="action-btn-small">Feedback</button>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <!-- Event Management Tab -->
            <div id="event-management" class="tab-pane">
                <div class="function-content">
                    <div class="active-events">
                        <h3>Active Events</h3>
                        <div class="events-grid">
                            {% for event in active_events %}
                            <div class="event-card">
                                <div class="event-header">
                                    <div class="event-info">
                                        <h4>{{ event.event_name }}</h4>
                                        <p class="organizer">{{ event.organizer_name }}</p>
                                        <p class="space">{{ event.space.name }}</p>
                                    </div>
                                    <div class="event-status">
                                        <span class="status">{{ event.get_status_display }}</span>
                                        <span class="progress">{{ event.progress }}% complete</span>
                                    </div>
                                </div>
                                
                                <div class="event-timeline">
                                    <div class="timeline-item">
                                        <span class="time">{{ event.start_time|time:"H:i" }}</span>
                                        <span class="activity">Event Start</span>
                                    </div>
                                    {% for milestone in event.milestones %}
                                    <div class="timeline-item {{ milestone.status }}">
                                        <span class="time">{{ milestone.time|time:"H:i" }}</span>
                                        <span class="activity">{{ milestone.activity }}</span>
                                    </div>
                                    {% endfor %}
                                    <div class="timeline-item">
                                        <span class="time">{{ event.end_time|time:"H:i" }}</span>
                                        <span class="activity">Event End</span>
                                    </div>
                                </div>
                                
                                <div class="event-services">
                                    <h5>Active Services</h5>
                                    {% for service in event.services %}
                                    <div class="service-item">
                                        <span class="service-name">{{ service.name }}</span>
                                        <span class="service-status">{{ service.get_status_display }}</span>
                                    </div>
                                    {% endfor %}
                                </div>
                                
                                <div class="event-actions">
                                    <button onclick="addService('{{ event.id }}')" class="action-btn-small">Add Service</button>
                                    <button onclick="updateProgress('{{ event.id }}')" class="action-btn-small">Update Progress</button>
                                    <button onclick="contactOrganizer('{{ event.id }}')" class="action-btn-small">Contact</button>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Calendar Tab -->
            <div id="calendar" class="tab-pane">
                <div class="function-content">
                    <div class="calendar-controls">
                        <div class="month-navigation">
                            <button onclick="previousMonth()" class="nav-btn">?</button>
                            <h3 id="current-month">{{ current_month|date:"F Y" }}</h3>
                            <button onclick="nextMonth()" class="nav-btn">?</button>
                        </div>
                        <div class="view-options">
                            <button class="view-btn active" onclick="setCalendarView('month')">Month</button>
                            <button class="view-btn" onclick="setCalendarView('week')">Week</button>
                            <button class="view-btn" onclick="setCalendarView('day')">Day</button>
                        </div>
                    </div>
                    
                    <div class="calendar-grid">
                        <!-- Calendar implementation would go here -->
                        <div class="calendar-placeholder">
                            <p>Calendar view showing all bookings and events</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function showTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
}
</script>
{% endblock %}
```

---

## 5. Day Visitors Section Page (/resort/day-visitors/)

### **Day Visitor Management**
```html
{% extends 'base.html' %}
{% block title %}Day Visitors - CampoPawa{% endblock %}

{% block content %}
<div class="function-page">
    {% include 'resort_portal/sidebar_resort.html' %}
    
    <div class="main-content">
        <div class="page-header">
            <h1>Day Visitors</h1>
            <div class="header-actions">
                <div class="quick-stats">
                    <div class="stat-item">
                        <span class="number">{{ current_visitors }}</span>
                        <span class="label">Current Visitors</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">{{ visitors_today }}</span>
                        <span class="label">Visitors Today</span>
                    </div>
                    <div class="stat-item">
                        <span class="number">KES {{ day_visitor_revenue }}</span>
                        <span class="label">Revenue Today</span>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Internal Navigation Tabs -->
        <div class="section-tabs">
            <button class="tab-btn active" onclick="showTab('visitor-check-in')">
                <span class="icon">?</span>
                <span>Visitor Check-in</span>
            </button>
            <button class="tab-btn" onclick="showTab('active-visitors')">
                <span class="icon">?</span>
                <span>Active Visitors</span>
            </button>
            <button class="tab-btn" onclick="showTab('facilities-usage')">
                <span class="icon">?</span>
                <span>Facilities Usage</span>
            </button>
            <button class="tab-btn" onclick="showTab('day-passes')">
                <span class="icon">?</span>
                <span>Day Passes</span>
            </button>
        </div>
        
        <!-- Tab Content Areas -->
        <div class="tab-content">
            <!-- Visitor Check-in Tab -->
            <div id="visitor-check-in" class="tab-pane active">
                <div class="function-content">
                    <div class="quick-check-in">
                        <h3>Quick Visitor Check-in</h3>
                        <form method="POST" class="visitor-check-in-form">
                            {% csrf_token %}
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Visitor Name *</label>
                                    <input type="text" name="visitor_name" required>
                                </div>
                                <div class="form-group">
                                    <label>Phone Number</label>
                                    <input type="tel" name="phone_number">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Visit Type *</label>
                                    <select name="visit_type" required>
                                        <option value="">Select type...</option>
                                        <option value="pool">Pool Access</option>
                                        <option value="spa">Spa Services</option>
                                        <option value="gym">Gym Access</option>
                                        <option value="restaurant">Restaurant Only</option>
                                        <option value="bar">Bar Only</option>
                                        <option value="full_day">Full Day Access</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Number of Guests *</label>
                                    <input type="number" name="number_of_guests" required min="1" max="20">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Expected Duration</label>
                                    <select name="duration">
                                        <option value="2_hours">2 Hours</option>
                                        <option value="4_hours">4 Hours</option>
                                        <option value="6_hours">6 Hours</option>
                                        <option value="full_day">Full Day</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Special Requirements</label>
                                    <input type="text" name="special_requirements" placeholder="Any special needs or requests">
                                </div>
                            </div>
                            <button type="submit" class="submit-btn">Check-in Visitor</button>
                        </form>
                    </div>
                    
                    <div class="day-pass-options">
                        <h3>Day Pass Options</h3>
                        <div class="passes-grid">
                            {% for pass in day_passes %}
                            <div class="pass-card">
                                <div class="pass-header">
                                    <h4>{{ pass.name }}</h4>
                                    <span class="price">KES {{ pass.price }}</span>
                                </div>
                                <div class="pass-features">
                                    {% for feature in pass.features %}
                                    <div class="feature-item">
                                        <span class="feature-name">{{ feature.name }}</span>
                                        <span class="feature-included">?</span>
                                    </div>
                                    {% endfor %}
                                </div>
                                <div class="pass-details">
                                    <p class="duration">{{ pass.duration }}</p>
                                    <p class="restrictions">{{ pass.restrictions }}</p>
                                </div>
                                <button onclick="selectPass('{{ pass.id }}')" class="action-btn-small">Select Pass</button>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Active Visitors Tab -->
            <div id="active-visitors" class="tab-pane">
                <div class="function-content">
                    <div class="visitors-controls">
                        <div class="filter-buttons">
                            <button class="filter-btn active" onclick="filterVisitors('all')">All Visitors</button>
                            <button class="filter-btn" onclick="filterVisitors('pool')">Pool</button>
                            <button class="filter-btn" onclick="filterVisitors('spa')">Spa</button>
                            <button class="filter-btn" onclick="filterVisitors('gym')">Gym</button>
                        </div>
                        <div class="search-box">
                            <input type="text" placeholder="Search visitors..." id="visitor-search">
                            <button class="search-btn">?</button>
                        </div>
                    </div>
                    
                    <div class="visitors-grid">
                        {% for visitor in active_visitors %}
                        <div class="visitor-card">
                            <div class="visitor-header">
                                <div class="visitor-info">
                                    <h4>{{ visitor.name }}</h4>
                                    <p class="visit-type">{{ visitor.get_visit_type_display }}</p>
                                    <p class="check-in-time">Checked in: {{ visitor.check_in_time|time:"H:i" }}</p>
                                    <p class="phone">{{ visitor.phone }}</p>
                                </div>
                                <div class="visitor-status">
                                    <span class="status">{{ visitor.get_status_display }}</span>
                                    <span class="duration">{{ visitor.duration_remaining }} remaining</span>
                                </div>
                            </div>
                            
                            <div class="visitor-details">
                                <div class="detail-item">
                                    <span class="label">Guests:</span>
                                    <span class="value">{{ visitor.number_of_guests }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Pass Type:</span>
                                    <span class="value">{{ visitor.day_pass.name }}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="label">Facilities Used:</span>
                                    <span class="value">{{ visitor.facilities_used|join:", " }}</span>
                                </div>
                            </div>
                            
                            <div class="visitor-actions">
                                <button onclick="extendVisit('{{ visitor.id }}')" class="action-btn-small">Extend Visit</button>
                                <button onclick="addService('{{ visitor.id }}')" class="action-btn-small">Add Service</button>
                                <button onclick="checkOut('{{ visitor.id }}')" class="action-btn-small">Check-out</button>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <!-- Facilities Usage Tab -->
            <div id="facilities-usage" class="tab-pane">
                <div class="function-content">
                    <div class="facilities-overview">
                        <h3>Facilities Usage Overview</h3>
                        <div class="facilities-grid">
                            {% for facility in facilities %}
                            <div class="facility-card">
                                <div class="facility-header">
                                    <h4>{{ facility.name }}</h4>
                                    <span class="capacity">{{ facility.current_usage }}/{{ facility.max_capacity }}</span>
                                </div>
                                <div class="facility-status">
                                    <div class="usage-bar">
                                        <div class="usage-fill" style="width: {{ facility.usage_percentage }}%"></div>
                                    </div>
                                    <span class="percentage">{{ facility.usage_percentage }}% occupied</span>
                                </div>
                                <div class="facility-details">
                                    <p class="wait-time">{{ facility.wait_time }} min wait</p>
                                    <p class="peak-hours">Peak: {{ facility.peak_hours }}</p>
                                </div>
                                <div class="facility-actions">
                                    <button onclick="viewDetails('{{ facility.id }}')" class="action-btn-small">View Details</button>
                                    <button onclick="manageQueue('{{ facility.id }}')" class="action-btn-small">Manage Queue</button>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="usage-analytics">
                        <h3>Usage Analytics</h3>
                        <div class="analytics-charts">
                            <div class="chart-container">
                                <h4>Peak Hours Analysis</h4>
                                <canvas id="peakHoursChart"></canvas>
                            </div>
                            <div class="chart-container">
                                <h4>Facility Popularity</h4>
                                <canvas id="popularityChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Day Passes Tab -->
            <div id="day-passes" class="tab-pane">
                <div class="function-content">
                    <div class="passes-management">
                        <h3>Day Pass Management</h3>
                        <div class="passes-controls">
                            <button onclick="openAddPassModal()" class="action-btn-small">Add New Pass</button>
                            <button onclick="viewPassAnalytics()" class="action-btn-small">View Analytics</button>
                        </div>
                        
                        <div class="passes-list">
                            {% for pass in day_passes %}
                            <div class="pass-item">
                                <div class="pass-header">
                                    <div class="pass-info">
                                        <h4>{{ pass.name }}</h4>
                                        <p class="description">{{ pass.description }}</p>
                                        <p class="validity">Valid for {{ pass.validity_period }}</p>
                                    </div>
                                    <div class="pass-pricing">
                                        <span class="price">KES {{ pass.price }}</span>
                                        <span class="sales">{{ pass.sales_today }} sold today</span>
                                    </div>
                                </div>
                                
                                <div class="pass-features">
                                    <h5>Included Facilities:</h5>
                                    <div class="features-list">
                                        {% for feature in pass.features %}
                                        <span class="feature-tag">{{ feature.name }}</span>
                                        {% endfor %}
                                    </div>
                                </div>
                                
                                <div class="pass-stats">
                                    <div class="stat-item">
                                        <span class="label">Total Sold:</span>
                                        <span class="value">{{ pass.total_sold }}</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="label">Revenue:</span>
                                        <span class="value">KES {{ pass.total_revenue }}</span>
                                    </div>
                                    <div class="stat-item">
                                        <span class="label">Avg. Rating:</span>
                                        <span class="value">{{ pass.average_rating }}/5</span>
                                    </div>
                                </div>
                                
                                <div class="pass-actions">
                                    <button onclick="editPass('{{ pass.id }}')" class="action-btn-small">Edit</button>
                                    <button onclick="viewSales('{{ pass.id }}')" class="action-btn-small">View Sales</button>
                                    <button onclick="toggleStatus('{{ pass.id }}')" class="action-btn-small">{{ pass.is_active|yesno:"Deactivate,Activate" }}</button>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
function showTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabId).classList.add('active');
    event.target.closest('.tab-btn').classList.add('active');
}
</script>
{% endblock %}
```

---

## 6. Enhanced Overview Dashboard

### **Complete Resort Operations Overview**
```html
<!-- Updated Overview Dashboard -->
<div class="overview-dashboard">
    <!-- Today's Summary Bar -->
    <div class="today-summary">
        <div class="summary-item">
            <div class="icon">?</div>
            <div class="info">
                <span class="number">{{ occupied_rooms }}</span>
                <span class="label">Rooms Occupied</span>
            </div>
        </div>
        <div class="summary-item">
            <div class="icon">?</div>
            <div class="info">
                <span class="number">{{ active_restaurant_tables }}</span>
                <span class="label">Restaurant Tables</span>
            </div>
        </div>
        <div class="summary-item">
            <div class="icon">?</div>
            <div class="info">
                <span class="number">{{ active_bar_customers }}</span>
                <span class="label">Bar Customers</span>
            </div>
        </div>
        <div class="summary-item">
            <div class="icon">?</div>
            <div class="info">
                <span class="number">{{ active_events }}</span>
                <span class="label">Active Events</span>
            </div>
        </div>
        <div class="summary-item">
            <div class="icon">?</div>
            <div class="info">
                <span class="number">{{ day_visitors }}</span>
                <span class="label">Day Visitors</span>
            </div>
        </div>
        <div class="summary-item">
            <div class="icon">?</div>
            <div class="info">
                <span class="number">KES {{ total_revenue }}</span>
                <span class="label">Total Revenue</span>
            </div>
        </div>
    </div>
    
    <!-- Quick Actions Grid -->
    <div class="quick-actions">
        <a href="{% url 'resort_portal:guests' %}" class="action-btn check-in">
            <div class="icon">?</div>
            <div class="text">
                <h3>Guest Check-In</h3>
                <p>30 seconds</p>
            </div>
        </a>
        
        <a href="{% url 'resort_portal:restaurant' %}" class="action-btn restaurant">
            <div class="icon">?</div>
            <div class="text">
                <h3>Restaurant</h3>
                <p>Table management</p>
            </div>
        </a>
        
        <a href="{% url 'resort_portal:bar' %}" class="action-btn bar">
            <div class="icon">?</div>
            <div class="text">
                <h3>Bar</h3>
                <p>Tabs & drinks</p>
            </div>
        </a>
        
        <a href="{% url 'resort_portal:events' %}" class="action-btn events">
            <div class="icon">?</div>
            <div class="text">
                <h3>Events & Spaces</h3>
                <p>Bookings</p>
            </div>
        </a>
        
        <a href="{% url 'resort_portal:day_visitors' %}" class="action-btn day-visitors">
            <div class="icon">?</div>
            <div class="text">
                <h3>Day Visitors</h3>
                <p>Check-in</p>
            </div>
        </a>
        
        <a href="{% url 'resort_portal:rooms' %}" class="action-btn rooms">
            <div class="icon">?</div>
            <div class="text">
                <h3>Room Status</h3>
                <p>Housekeeping</p>
            </div>
        </a>
    </div>
    
    <!-- Recent Activity Feed -->
    <div class="recent-activity">
        <h3>Recent Activity</h3>
        <div class="activity-list">
            {% for activity in recent_activities|slice:":8" %}
            <div class="activity-item">
                <div class="activity-icon">{{ activity.icon }}</div>
                <div class="activity-content">
                    <div class="activity-header">
                        <span class="activity-title">{{ activity.title }}</span>
                        <span class="activity-time">{{ activity.time_ago }}</span>
                    </div>
                    <div class="activity-description">{{ activity.description }}</div>
                    <div class="activity-category">{{ activity.get_category_display }}</div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Alerts & Notifications -->
    <div class="alerts-section">
        {% if vip_arrivals > 0 %}
        <div class="alert vip-alert">
            <div class="alert-icon">?</div>
            <div class="alert-content">
                <h4>VIP Arrivals Today</h4>
                <p>{{ vip_arrivals }} VIP guests arriving</p>
                <a href="{% url 'resort_portal:vip_list' %}" class="alert-action">View List</a>
            </div>
        </div>
        {% endif %}
        
        {% if restaurant_queue > 0 %}
        <div class="alert restaurant-alert">
            <div class="alert-icon">?</div>
            <div class="alert-content">
                <h4>Restaurant Queue</h4>
                <p>{{ restaurant_queue }} parties waiting for tables</p>
                <a href="{% url 'resort_portal:restaurant' %}" class="alert-action">Manage Queue</a>
            </div>
        </div>
        {% endif %}
        
        {% if upcoming_events > 0 %}
        <div class="alert events-alert">
            <div class="alert-icon">?</div>
            <div class="alert-content">
                <h4>Upcoming Events</h4>
                <p>{{ upcoming_events }} events starting today</p>
                <a href="{% url 'resort_portal:events' %}" class="alert-action">View Events</a>
            </div>
        </div>
        {% endif %}
    </div>
</div>
```

---

## 7. URL Structure Update

### **Complete Resort Operations URLs**
```python
# resort_portal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Overview
    path('', views.overview, name='overview'),
    
    # Guest Operations
    path('guests/', views.guests_section, name='guests'),
    path('rooms/', views.rooms_section, name='rooms'),
    
    # Customer Operations
    path('restaurant/', views.restaurant_section, name='restaurant'),
    path('bar/', views.bar_section, name='bar'),
    path('events/', views.events_section, name='events'),
    path('day-visitors/', views.day_visitors_section, name='day_visitors'),
    
    # Services (Combined)
    path('services/', views.services_section, name='services'),
    
    # Reports (Manager Only)
    path('reports/', views.reports_section, name='reports'),
    
    # Settings
    path('settings/', views.settings_section, name='settings'),
]
```

---

## 8. Benefits of Complete Resort Management

### **Comprehensive Operations Coverage**
- **Room Guests** - Traditional hotel operations
- **Restaurant Customers** - Dining, events, casual dining
- **Bar Patrons** - Drinks, entertainment, social gatherings
- **Event Spaces** - Meetings, conferences, weddings, parties
- **Day Visitors** - Pool, spa, gym, facilities access

### **Unified Management Platform**
- **Single dashboard** for all resort operations
- **Cross-department analytics** and insights
- **Centralized customer data** across all touchpoints
- **Integrated billing** and revenue tracking
- **Staff coordination** across departments

### **Enhanced Customer Experience**
- **Seamless service** across all resort facilities
- **Unified customer profiles** and preferences
- **Cross-selling opportunities** between departments
- **Loyalty program** integration
- **Personalized experiences** based on usage patterns

### **Operational Efficiency**
- **Real-time visibility** into all operations
- **Resource optimization** across facilities
- **Staff scheduling** based on demand patterns
- **Inventory management** for all departments
- **Performance analytics** for continuous improvement

---

## Conclusion

This comprehensive design transforms the resort dashboard from a room-focused system to a **complete resort operations platform** that manages all customer types and revenue streams.

**Key Features:**
- **Complete customer coverage** - rooms, restaurant, bar, events, day visitors
- **Unified management** - single platform for all operations
- **Real-time insights** - cross-department analytics and visibility
- **Enhanced customer experience** - seamless service across all facilities
- **Scalable architecture** - easy to add new services and facilities

**Implementation Priority:**
1. **Week 1**: Overview dashboard with all operations
2. **Week 2**: Restaurant and bar sections
3. **Week 3**: Events and day visitor sections
4. **Week 4**: Integration and analytics

This approach provides resorts with a **complete operational management system** that maximizes revenue opportunities and enhances customer satisfaction across all touchpoints.

**Ready for comprehensive resort management!**
