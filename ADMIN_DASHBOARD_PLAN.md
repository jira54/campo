# CampoPawa Admin Dashboard Plan

## Overview
Comprehensive admin dashboard for monitoring users, managing subscriptions, and handling payments manually when M-Pesa paybill is not available.

## Current System Analysis

### User Model (Vendor)
- **Business Info**: `business_name`, `email`, `phone_number`, `business_type`
- **Plan Status**: `is_premium`, `trial_end_date`, `subscription.plan`
- **Business Types**: Food, Printing, Thrift, Rental, Cakes, NGO, Resort, Other
- **Authentication**: Email-based with 2FA support

### Subscription System
- **Plans Available**:
  - `free` - Free Tier (KES 0)
  - `premium_retail` - Retail Pro (KES 700/mo)
  - `enterprise_ngo` - Enterprise NGO (KES 3,500/mo)
  - `enterprise_resort` - Enterprise Resort (KES 3,500/mo)
- **Payment Tracking**: `Payment` model with M-Pesa integration
- **Trial System**: `trial_end_date` field for trial periods
- **Subscription Model**: One-to-one relationship with Vendor

### Payment System
- **M-Pesa Integration**: STK Push and Till Payment support
- **Payment Status**: pending, confirmed, failed
- **Invoice Generation**: Automatic invoice numbering for confirmed payments
- **Manual Payment Entry**: Currently limited - needs enhancement

---

## Admin Dashboard Structure

### 1. Overview Dashboard
**Purpose**: High-level view of platform health and performance

**Key Metrics**:
- **Total Users**: Count of all registered vendors
- **Active Subscriptions**: Breakdown by plan (free vs premium)
- **Revenue**: Monthly/total payments (KES)
- **New Signups**: Today/This week/This month
- **Trial Users**: Active trials vs expired trials
- **Payment Success Rate**: Confirmed vs failed payments

**Visualizations**:
- **User Growth Chart**: New users over time (line chart)
- **Revenue Trends**: Monthly revenue (bar chart)
- **Plan Distribution**: Pie chart of plan types
- **Business Type Breakdown**: Which industries use CampoPawa
- **Payment Status**: Confirmed vs pending vs failed

**Recent Activity Feed**:
- Latest user registrations
- Recent plan changes
- New payments (confirmed/pending)
- Trial extensions/expirations

---

### 2. User Management
**Purpose**: Comprehensive user administration and manual tier assignment

#### User List View
**Display Columns**:
- Business Name
- Email
- Phone Number
- Business Type
- Current Plan
- Trial Status
- Account Status (Active/Inactive)
- Registration Date
- Last Login

**Filtering & Search**:
- Search by email, business name, phone number
- Filter by plan (free, premium_retail, enterprise_ngo, enterprise_resort)
- Filter by business type
- Filter by trial status (active trial, no trial, expired trial)
- Filter by account status
- Date range filters

**Quick Actions**:
- View user details
- Change subscription plan
- Extend trial
- Activate/deactivate account
- Send password reset

#### User Detail View
**User Information**:
- Business details (name, type, location)
- Contact information (email, phone, physical address)
- Branding (logo, accent color)
- Business type custom field
- Registration and login history

**Subscription Information**:
- Current plan and expiry date
- Trial status and end date
- Payment history
- Plan change history

**Business Analytics**:
- Customer count (if retail)
- Property count (if multi-location)
- Usage statistics
- Activity logs

#### Manual Tier Assignment
**Features**:
- **Plan Selection**: Dropdown with all available plans
- **Duration Options**:
  - 1 month
  - 3 months
  - 6 months
  - 1 year
  - Indefinite (no expiry)
- **Reason/Notes**: Why manual assignment (e.g., "Bank transfer payment", "Complimentary upgrade")
- **Payment Method**: Bank transfer, cash, check, other
- **Amount**: For manual payment entry
- **Effective Date**: When the plan change takes effect

**Workflow**:
1. Select user from list
2. Click "Change Plan" button
3. Choose new plan and duration
4. Enter payment details (if applicable)
5. Add notes/reason
6. Confirm change
7. System updates subscription + creates payment record

#### Trial Management
**Features**:
- **Extend Trial**: Add days/weeks to existing trial
- **Convert to Paid**: Move from trial to paid plan
- **Cancel Trial**: Downgrade to free immediately
- **Trial Analytics**: Track trial conversion rates

**Trial Extension Options**:
- Add 7 days
- Add 14 days
- Add 30 days
- Custom duration
- Set specific end date

#### Bulk Operations
**Features**:
- **Bulk Plan Upgrade**: Select multiple users → upgrade to same plan
- **Bulk Trial Extension**: Extend trials for multiple users
- **Bulk Deactivation**: Deactivate multiple accounts
- **Bulk Email**: Send notifications to selected users

---

### 3. Payment Management
**Purpose**: Monitor and manage all payment transactions

#### Payment History View
**Display Columns**:
- Invoice Number
- Vendor (Business Name)
- Amount (KES)
- Plan Paid For
- Payment Method (M-Pesa, Manual)
- Status (Pending, Confirmed, Failed)
- Transaction Date
- M-Pesa Reference (if applicable)

**Filtering**:
- Filter by status (pending, confirmed, failed)
- Filter by payment method
- Filter by plan type
- Date range filters
- Search by invoice number or vendor name

**Actions**:
- View payment details
- Confirm pending payment
- Reject pending payment
- View associated vendor
- Download invoice

#### Manual Payment Entry
**Purpose**: Add payments from non-M-Pesa sources (bank transfers, cash, etc.)

**Form Fields**:
- **Vendor**: Search and select vendor
- **Amount**: Payment amount in KES
- **Payment Method**: Bank transfer, Cash, Check, Other
- **Plan Paid For**: Select plan this payment covers
- **Transaction Reference**: Bank reference, receipt number, etc.
- **Payment Date**: When payment was made
- **Notes**: Additional details

**Workflow**:
1. Click "Add Manual Payment"
2. Search and select vendor
3. Enter payment details
4. Select plan this payment covers
5. Add transaction reference
6. Confirm payment
7. System updates subscription + creates payment record

#### Payment Status Management
**Pending Payments**:
- View all pending payments
- Confirm payment (updates subscription)
- Reject payment (marks as failed)
- Request additional information

**Failed Payments**:
- View failed payment details
- Retry payment processing
- Contact vendor
- Mark as resolved

#### Revenue Reports
**Features**:
- **Monthly Revenue**: Revenue by month
- **Plan Revenue**: Revenue breakdown by plan type
- **Payment Method Analysis**: M-Pesa vs manual payments
- **Growth Trends**: Revenue growth over time
- **Export**: Download CSV/PDF reports

---

### 4. Business Analytics
**Purpose**: Understand platform usage and business insights

#### User Analytics
- **User Growth**: New users over time
- **User Retention**: Active vs inactive users
- **Trial Conversion**: Trial to paid conversion rate
- **Churn Analysis**: Users canceling or downgrading

#### Business Type Analysis
- **Industry Distribution**: Which business types use CampoPawa
- **Plan by Industry**: Which plans different industries choose
- **Revenue by Industry**: Revenue contribution by business type

#### Geographic Analysis
- **User Locations**: Where users are based
- **Regional Performance**: Revenue by region
- **Property Distribution**: Multi-location user properties

---

### 5. Security & Permissions
**Purpose**: Ensure admin dashboard is secure and auditable

#### Access Control
- **Superuser Only**: Only Django superusers can access admin dashboard
- **Role-Based Access**: Future expansion for different admin roles
- **IP Whitelist**: Optional restriction to specific IPs

#### Activity Logging
- **Log All Admin Actions**:
  - User plan changes
  - Trial extensions
  - Manual payments
  - Account activations/deactivations
  - Bulk operations

#### Audit Trail
- **Who**: Which admin performed the action
- **What**: What action was performed
- **When**: Timestamp of action
- **Why**: Reason/notes for the action
- **Impact**: Before/after state changes

---

## Implementation Plan

### Phase 1: Admin Dashboard Infrastructure
**Duration**: 2-3 days

**Tasks**:
1. **Create Admin App**: `python manage.py startapp admin_dashboard`
2. **Admin Authentication**: Middleware to restrict to superusers only
3. **URL Configuration**: Set up `/admin/` routes
4. **Base Templates**: Admin layout, sidebar, navigation
5. **Static Files**: Admin-specific CSS/JS

**Deliverables**:
- Admin app structure
- Authentication middleware
- Base admin templates
- URL routing

---

### Phase 2: Overview Dashboard
**Duration**: 3-4 days

**Tasks**:
1. **Dashboard View**: Main admin landing page
2. **Statistics Cards**: Total users, revenue, active subscriptions
3. **Charts Implementation**: User growth, revenue trends, plan distribution
4. **Recent Activity Feed**: Latest signups, payments, plan changes
5. **Data Aggregation**: Efficient database queries for statistics

**Deliverables**:
- Overview dashboard view
- Statistics cards with real-time data
- Interactive charts
- Activity feed

---

### Phase 3: User Management
**Duration**: 5-7 days

**Tasks**:
1. **User List View**: Paginated table with filters
2. **User Detail View**: Complete user profile
3. **Plan Change Form**: Manual tier assignment
4. **Trial Management**: Extend/cancel trials
5. **Bulk Operations**: Multiple user actions
6. **Search & Filter**: Advanced user search functionality

**Deliverables**:
- User list with filtering
- User detail view
- Plan change functionality
- Trial management
- Bulk operations

---

### Phase 4: Payment Management
**Duration**: 4-5 days

**Tasks**:
1. **Payment History View**: All transactions with filters
2. **Manual Payment Entry**: Add non-M-Pesa payments
3. **Payment Status Management**: Confirm/reject pending payments
4. **Revenue Reports**: Export payment data
5. **Invoice Generation**: PDF invoices for manual payments

**Deliverables**:
- Payment history view
- Manual payment entry form
- Payment status management
- Revenue reports
- Invoice generation

---

### Phase 5: Security & Permissions
**Duration**: 2-3 days

**Tasks**:
1. **Admin Middleware**: Restrict to superusers only
2. **Activity Logging**: Track admin actions
3. **Audit Trail**: Who changed what and when
4. **Security Headers**: CSRF protection, secure cookies
5. **Rate Limiting**: Prevent abuse of admin endpoints

**Deliverables**:
- Secure admin access
- Activity logging system
- Audit trail
- Security enhancements

---

## Database Schema Changes

### New Models

#### AdminActivityLog
```python
class AdminActivityLog(models.Model):
    admin = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE)
    action = models.CharField(max_length=100)  # e.g., 'plan_changed', 'trial_extended'
    target_user = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    description = models.TextField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
```

#### ManualPayment
```python
class ManualPayment(models.Model):
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='manual_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plan_paid_for = models.CharField(max_length=20, choices=PLAN_CHOICES)
    payment_method = models.CharField(max_length=50)  # Bank transfer, Cash, Check, etc.
    transaction_reference = models.CharField(max_length=100)
    payment_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey('vendors.Vendor', on_delete=models.SET_NULL, null=True, related_name='created_manual_payments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
```

### Model Modifications

#### Subscription Model
- Add `assigned_by` field to track who manually assigned the plan
- Add `assignment_reason` field for manual assignments
- Add `manual_override` boolean to indicate manual vs automatic assignment

---

## API Endpoints

### User Management
- `GET /admin/api/users/` - List all users with filters
- `GET /admin/api/users/<id>/` - Get user details
- `POST /admin/api/users/<id>/change-plan/` - Change user plan
- `POST /admin/api/users/<id>/extend-trial/` - Extend user trial
- `POST /admin/api/users/bulk-action/` - Bulk operations

### Payment Management
- `GET /admin/api/payments/` - List all payments
- `POST /admin/api/payments/manual/` - Add manual payment
- `POST /admin/api/payments/<id>/confirm/` - Confirm payment
- `POST /admin/api/payments/<id>/reject/` - Reject payment

### Analytics
- `GET /admin/api/analytics/overview/` - Overview statistics
- `GET /admin/api/analytics/revenue/` - Revenue analytics
- `GET /admin/api/analytics/users/` - User analytics

---

## UI/UX Considerations

### Design Principles
- **Clean & Professional**: Business-focused interface
- **Fast Performance**: Quick page loads and data retrieval
- **Mobile Responsive**: Works on tablets and phones
- **Intuitive Navigation**: Easy to find features
- **Clear Feedback**: Success/error messages for all actions

### Color Scheme
- **Primary**: Professional blue (#2563EB)
- **Success**: Green (#10B981)
- **Warning**: Orange (#F59E0B)
- **Danger**: Red (#EF4444)
- **Neutral**: Grays for text and backgrounds

### Key UI Components
- **Data Tables**: Sortable, filterable, with pagination
- **Forms**: Clean validation, clear error messages
- **Modals**: For quick actions (plan change, trial extension)
- **Charts**: Interactive, responsive charts using Chart.js
- **Notifications**: Toast notifications for action feedback

---

## Testing Strategy

### Unit Tests
- Admin authentication middleware
- User management functions
- Payment processing logic
- Statistics calculations

### Integration Tests
- Admin workflow end-to-end
- Plan change and subscription update
- Manual payment and subscription activation
- Trial extension and expiry

### Security Tests
- Access control (non-superusers blocked)
- CSRF protection
- SQL injection prevention
- XSS prevention

---

## Deployment Considerations

### Database Migrations
- Create new models (AdminActivityLog, ManualPayment)
- Modify existing models (Subscription)
- Run migrations on production database

### Environment Variables
- No new environment variables required
- Uses existing Django settings

### Performance Optimization
- Database indexing for admin queries
- Caching for statistics calculations
- Pagination for large datasets
- Lazy loading for user details

---

## Future Enhancements

### Phase 6 (Future)
- **Email Notifications**: Automated emails for plan changes, trial expirations
- **Export Functionality**: Export user data, payment data to CSV/Excel
- **Advanced Analytics**: Cohort analysis, churn prediction
- **Multi-Admin Support**: Different admin roles with different permissions
- **API Documentation**: Swagger/OpenAPI documentation for admin API
- **Mobile App**: Native mobile app for admin on-the-go

---

## Success Metrics

### Key Performance Indicators
- **Admin Efficiency**: Time to complete common tasks
- **User Satisfaction**: Feedback from admins using the dashboard
- **Revenue Impact**: Increase in manual payments and plan upgrades
- **Data Accuracy**: Accuracy of manual payment entry and plan assignments
- **System Reliability**: Uptime and error rates

### Monitoring
- **Admin Actions**: Track admin activity volume
- **Error Rates**: Monitor failed operations
- **Performance**: Page load times, API response times
- **Security**: Monitor unauthorized access attempts

---

## Conclusion

This admin dashboard will provide comprehensive control over user management, subscription handling, and payment processing. It enables manual tier assignment when M-Pesa paybill is not available, ensuring business continuity and revenue collection through alternative payment methods.

The phased implementation approach ensures quick wins (Phase 1-2) while building toward a complete solution (Phase 3-5). The modular design allows for future enhancements and scalability as the platform grows.
