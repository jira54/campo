from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages

from .decorators import ngo_enterprise_required
from .models import Beneficiary, Program, Intervention

@login_required
@ngo_enterprise_required
def ngo_dashboard(request):
    """Boutique Impact Dashboard with M&E Intelligence."""
    from django.db.models import Count
    vendor = request.user
    
    try:
        # Core Volume
        total_beneficiaries = Beneficiary.objects.filter(vendor=vendor).count()
        active_programs = Program.objects.filter(vendor=vendor, is_active=True).count()
        total_interventions = Intervention.objects.filter(vendor=vendor).count()
        
        # 1. Demographics: Gender Diversity Index
        gender_stats = Beneficiary.objects.filter(vendor=vendor).values('sex').annotate(count=Count('sex'))
        
        # 2. Resilience: Vulnerability Heatmap
        vulnerability_stats = Beneficiary.objects.filter(vendor=vendor).values('vulnerability_marker').annotate(count=Count('vulnerability_marker'))
        
        # 3. Reach: Regional Top 5 (Counties)
        regional_stats = Beneficiary.objects.filter(vendor=vendor).values('county').annotate(count=Count('county')).order_by('-count')[:5]
        
        # 4. Program Impact: Actual Reach vs Target
        programs = Program.objects.filter(vendor=vendor).annotate(actual_reach=Count('interventions__beneficiary', distinct=True))
        program_data = []
        for p in programs:
            progress = round((p.actual_reach / p.target_beneficiaries_count * 100)) if p.target_beneficiaries_count > 0 else 0
            program_data.append({
                'name': p.name,
                'target': p.target_beneficiaries_count,
                'actual': p.actual_reach,
                'progress': progress
            })

        context = {
            'total_beneficiaries': total_beneficiaries,
            'active_programs': active_programs,
            'total_interventions': total_interventions,
            'gender_stats': gender_stats,
            'vulnerability_stats': vulnerability_stats,
            'regional_stats': regional_stats,
            'program_data': program_data,
        }
    except Exception as e:
        context = {
            'total_beneficiaries': 0, 'active_programs': 0, 'total_interventions': 0,
            'gender_stats': [], 'vulnerability_stats': [], 'regional_stats': [],
            'program_data': [], 'critical_error': str(e)
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
    Global Standard: Export unique anonymized IDs, demographics, and activities (no Personal Names).
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

@login_required
@ngo_enterprise_required
def add_program(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        donor = request.POST.get('donor')
        target = request.POST.get('target', 0)
        
        Program.objects.create(
            vendor=request.user,
            name=name,
            donor=donor,
            target_beneficiaries_count=target
        )
        messages.success(request, "A new vision has been seeded! Program created successfully. ✨")
        return redirect('ngo_portal:dashboard')
    return render(request, 'ngo_portal/add_program.html')


@login_required
@ngo_enterprise_required
def add_beneficiary(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        sex = request.POST.get('sex')
        county = request.POST.get('county')
        vulnerability = request.POST.get('vulnerability', 'none')
        
        Beneficiary.objects.create(
            vendor=request.user,
            name=name,
            phone=phone,
            sex=sex,
            county=county,
            vulnerability_marker=vulnerability
        )
        messages.success(request, "A new life added to the standard of care. Beneficiary registered beautifully. 🌸")
        return redirect('ngo_portal:beneficiaries')
    return render(request, 'ngo_portal/add_beneficiary.html')


@login_required
@ngo_enterprise_required
def log_activity(request):
    vendor = request.user
    if request.method == 'POST':
        ben_id = request.POST.get('beneficiary_id')
        prog_id = request.POST.get('program_id')
        activity = request.POST.get('activity_type')
        notes = request.POST.get('notes')
        
        try:
            beneficiary = Beneficiary.objects.get(id=ben_id, vendor=vendor)
            program = Program.objects.get(id=prog_id, vendor=vendor)
            
            Intervention.objects.create(
                vendor=vendor,
                beneficiary=beneficiary,
                program=program,
                activity_type=activity,
                notes=notes
            )
            messages.success(request, "Impact beautifully recorded. Every act of care matters. ✨")
            return redirect('ngo_portal:dashboard')
        except (Beneficiary.DoesNotExist, Program.DoesNotExist):
            messages.error(request, "Hmm, we couldn't find those records. Please try again with love.")
            
    beneficiaries = Beneficiary.objects.filter(vendor=vendor)
    programs = Program.objects.filter(vendor=vendor)
    return render(request, 'ngo_portal/log_activity.html', {
        'beneficiaries': beneficiaries,
        'programs': programs
    })
