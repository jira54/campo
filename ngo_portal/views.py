import csv
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .decorators import ngo_enterprise_required
from .models import Beneficiary, Program, Intervention

@login_required
@ngo_enterprise_required
def ngo_dashboard(request):
    vendor = request.user
    total_beneficiaries = Beneficiary.objects.filter(vendor=vendor).count()
    active_programs = Program.objects.filter(vendor=vendor, is_active=True).count()
    total_interventions = Intervention.objects.filter(vendor=vendor).count()

    context = {
        'total_beneficiaries': total_beneficiaries,
        'active_programs': active_programs,
        'total_interventions': total_interventions,
        # add more M&E metrics here later
    }
    return render(request, 'ngo_portal/dashboard.html', context)


@login_required
@ngo_enterprise_required
def beneficiary_list(request):
    vendor = request.user
    beneficiaries = Beneficiary.objects.filter(vendor=vendor).order_by('-added_at')
    return render(request, 'ngo_portal/beneficiaries.html', {'beneficiaries': beneficiaries})


@login_required
@ngo_enterprise_required
def export_donor_audit(request):
    """
    1-Click Donor Compliant CSV Export
    USAID Standard: Export unique anonymized IDs, demographics, and activities (no PII Names).
    """
    vendor = request.user
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ME_Donor_Audit.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Unique_ID', 'Sex', 'Age_Bracket', 'County', 'Sub_County', 
        'Vulnerability', 'Intervention_Date', 'Program', 'Activity_Type'
    ])

    interventions = Intervention.objects.filter(vendor=vendor).select_related('beneficiary', 'program').order_by('-date_executed')

    for inter in interventions:
        ben = inter.beneficiary
        # Calculate Age Bracket logic simply for the CSV
        age_bracket = 'Unknown'
        if ben.date_of_birth:
            # Simple approximation
            import datetime
            age = (datetime.date.today() - ben.date_of_birth).days // 365
            age_bracket = '<18' if age < 18 else '18+'

        writer.writerow([
            ben.unique_system_id,
            ben.get_sex_display(),
            age_bracket,
            ben.county,
            ben.sub_county,
            ben.get_vulnerability_marker_display(),
            inter.date_executed.strftime('%Y-%m-%d'),
            inter.program.name,
            inter.activity_type
        ])

    return response
