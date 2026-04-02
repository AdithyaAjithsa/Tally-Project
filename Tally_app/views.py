from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from Tally_app.models import State,Country,Company,GSTDetails,GSTRateDetails,TDSDeductorDetails,TCSCollectorDetails,VATDetails,ExciseDetails,ServiceTaxDetails,ServiceTaxRate,PayrollStatutoryDetails,CompanyAddress,MerchantProfile,CompanyFeatures,DateRange,CurrentDate,TallyVaultSetting,Scenario,ListOfVoucherType,Currency,CostCategory,RateOfExchange,Unit,Godowns
from django.contrib.auth.hashers import make_password,check_password
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from Tally_app.models import GSTEffectiveDate,GSTSettings,TDSPersonResponsibleDetail,SlabRate,TCSPersonResponsibleDetail,VATTaxRate,ExciseTariffDetail,NewUsers,SecuritySettings,Classification
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode
from urllib.parse import urlparse, parse_qs
import json



# Create your views here.

def index(request):
    set_default_states_and_countries()
    return render(request, 'index.html')


def Log_in(request):
    return render(request,'login.html')


def registration(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        pswd = request.POST['pswd']
        confirmpswd = request.POST['confirmpswd']

        if pswd != confirmpswd:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=name).exists():
            messages.error(request, "Username already taken")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use")
            return redirect('register')

        user = User.objects.create_user(username=name, email=email, password=pswd)
        user.save()
        messages.success(request, "Registration successful. You can now log in.")
        return redirect('Log_in')  

    return render(request, 'index.html')  



def Fun_login(request):
    if request.method == 'POST':
        username=request.POST['username']
        password=request.POST['pswd']
        user1=auth.authenticate(username=username,password=password)
        if user1 is not None:
            # request.session["uid"] = user1.id
            if user1.is_staff:
                login(request,user1)
                return redirect('Log_in')
            else:
                auth.login(request,user1)
                request.session['vault_force_check'] = True
                return redirect('userDashboard')
        else:
            messages.info(request,'Invalid Username or Password')
            return redirect('Log_in')
    return render(request,'login.html')



def userDashboard(request):
    if request.session.pop('vault_force_check', False):
        request.session['vault_authenticated_company_ids'] = []
        request.session['vault_modal_shown_once'] = False 

    last_date_range = DateRange.objects.filter(user=request.user).order_by('-id').first()
    last_current_date = CurrentDate.objects.filter(user=request.user).order_by('-id').first()
    companies = Company.objects.filter(user=request.user).order_by('-id')

    vault_companies = Company.objects.filter(
        user=request.user,
        tallyvaultsetting__isnull=False
    )

    unlocked_company_ids = request.session.get('vault_authenticated_company_ids', [])
    show_vault_login = False

    modal_shown = request.session.get('vault_modal_shown_once', False)

    if not modal_shown:
        for company in vault_companies:
            if company.id not in unlocked_company_ids:
                show_vault_login = True
                request.session['vault_modal_shown_once'] = True 
                break

    context = {
        'last_date_range': last_date_range.date_range if last_date_range else None,
        'last_current_date': last_current_date.current_date if last_current_date else None,
        'companies': companies,
        'vault_companies': vault_companies,
        'show_vault_login': show_vault_login,
    }
    return render(request, 'user_dashboard.html', context)



def masters_create(request):
    return render(request,'masters/masters_create.html')

def masters_alter(request):
    return render(request,'masters/masters_alter.html')

def masters_chart_of_accounts(request):
    return render(request,'masters/masters_chart_of_accounts.html')

def imported_bank_data(request):
    return render(request,'bank/imported_bank_data.html')

def cheque_printing(request):
    return render(request,'bank/cheque_printing.html')

def post_dated_summary(request):
    return render(request,'bank/post_dated_summary.html')

def deposit_slip(request):
    return render(request,'bank/deposit_slip.html')

def payment_advance(request):
    return render(request,'bank/payment_advance.html')

def account_books_ledger(request):
    return render(request,'account_books/ledger.html')

def group_summary(request):
    return render(request,'account_books/group_summary.html')

def group_vouchers(request):
    return render(request,'account_books/group_vouchers.html')

def stock_item(request):
    return render(request,'inventory_book/stock_item.html')

def location(request):
    return render(request,'inventory_book/location.html')

def stock_group_summary(request):
    return render(request,'inventory_book/stock_group_summary.html')

def stock_category_summary(request):
    return render(request,'inventory_book/stock_category_summary.html')

def stock_query(request):
    return render(request,'statement_of_inventory/stock_query.html')

def stock_group_analysis(request):
    return render(request,'statement_of_inventory/movement_analysis/stock_group_analysis.html')

def stock_group_category(request):
    return render(request,'statement_of_inventory/movement_analysis/stock_group_category.html')

def stock_item_analysis(request):
    return render(request,'statement_of_inventory/movement_analysis/stock_item_analysis.html')

def group_analysis(request):
    return render(request,'statement_of_inventory/movement_analysis/group_analysis.html')

def ledger_analysis(request):
    return render(request,'statement_of_inventory/movement_analysis/ledger_analysis.html')

def transfer_analysis(request):
    return render(request,'statement_of_inventory/movement_analysis/transfer_analysis.html')

def ageing_analysis(request):
    return render(request,'statement_of_inventory/ageing_analysis.html')

def cost_estimation(request):
    return render(request,'statement_of_inventory/cost_estimation.html')

def gst_rate_setup(request):
    return render(request,'statutory_reports/gst_utilities/gst_rate_setup.html')

def validate_party(request):
    return render(request,'statutory_reports/gst_utilities/validate_party.html')

def create_party(request):
    return render(request,'statutory_reports/gst_utilities/create_party.html')

def update_party_msme_details(request):
    return render(request,'statutory_reports/msme_reports/update_party_msme_details.html')

def pay_slip(request):
    return render(request,'payroll/pay_slip.html')

def pay_sheet(request):
    return render(request,'payroll/pay_sheet.html')

def payment_advice(request):
    return render(request,'payroll/payment_advice.html')

def payroll_statement(request):
    return render(request,'payroll/payroll_statement.html')

def employee_pay_head_breakup(request):
    return render(request,'payroll/employee_pay_head_breakup.html')

def pay_head_employee_breakup(request):
    return render(request,'payroll/pay_head_employee_breakup.html')

def employee_profile(request):
    return render(request,'payroll/employee_profile.html')



def create_company_page(request):
    states = State.objects.all()
    countries = Country.objects.all()
    show = request.GET.get('show', '')
    return render(request,'company/create_company.html', {
        'states': states,
        'countries': countries,
        'show': show,
    })



def create_new_state(request):
    if request.method == 'POST':
        state = request.POST.get('state')
        if state:
            State.objects.create(name=state)
    return redirect('/create_company_page/?show=state')


def create_new_country(request):
    if request.method == 'POST':
        country = request.POST.get('country')
        if country:
            Country.objects.create(name=country)
    return redirect('/create_company_page/?show=country')



def company_features(request):
    latest_company = Company.objects.order_by('-id').first()
    return render(request,'company/company_features.html',{ 'latest_company': latest_company})



def gst_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    states = State.objects.all()

    gst_details = GSTDetails.objects.filter(company=company).first()

    next_page = request.GET.get('next')
    show = request.GET.get('show', '') 
    current_date_obj = CurrentDate.objects.filter(user=request.user).first()
    current_date = current_date_obj.current_date if current_date_obj else None     
    context = {
        'states': states,'company_id': company.id,'gst_details': gst_details,'next': next_page, 
        'show':show,'current_date': current_date,
    }
    return render(request, 'company/gst_details.html', context)


def create_new_state_gst(request):
    if request.method == 'POST':
        state = request.POST.get('state')
        company_id = request.POST.get('company_id')
        if state:
            State.objects.create(name=state)
        return redirect(f'/gst_details/{company_id}/?show=state')



def company_tds_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    tds_details = TDSDeductorDetails.objects.filter(company=company).first()
    next_page = request.GET.get('next')
    return render(request, 'company/company_tds_details.html', {
        'company_id': company_id,'tds_details': tds_details,'next': next_page, 
    })



def company_tcs_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    tcs_details = TCSCollectorDetails.objects.filter(company=company).first()
    next_page = request.GET.get('next')

    return render(request, 'company/company_tcs_details.html', {
        'company_id': company_id,'tcs_details': tcs_details,'next': next_page, 
    })


def vat_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    vat_details = VATDetails.objects.filter(company=company).first()
    next_page = request.GET.get('next')
    states = State.objects.all()
    return render(request, 'company/vat_details.html', {
        'company_id': company_id,'vat_details': vat_details,'next': next_page,'states': states,'company':company 
    })


def create_new_state_vat(request):
    if request.method == 'POST':
        state_name = request.POST.get('state')
        company_id = request.POST.get('company_id')
        next_page = request.POST.get('next', '')

        if state_name:
            new_state = State.objects.create(name=state_name)

            params = request.POST.copy()
            params['new_state'] = new_state.name
            params['show'] = 'state'
            query_string = urlencode(params)

            return redirect(f'/vat_details/{company_id}/?{query_string}')

    return redirect('/')


def excise_details(request, company_id):
    states = State.objects.all()
    company = get_object_or_404(Company, id=company_id)
    excise_details = ExciseDetails.objects.filter(company=company).first()
    next_page = request.GET.get('next')
    show = request.GET.get('show', '') 
    referer = request.META.get('HTTP_REFERER', '')
    from_next = ''
    if referer:
        parsed = urlparse(referer)
        query = parse_qs(parsed.query)
        if query.get('next', [None])[0] == 'alter':
            from_next = 'alter'

    return render(request, 'company/excise_details.html', {
        'states': states,'company_id': company_id,'excise_details': excise_details,'next': next_page,'show':show,'company':company,'from_next': from_next,

    })


def create_new_state_excise(request):
    if request.method == 'POST':
        state_name = request.POST.get('state')
        company_id = request.POST.get('company_id')
        next_page = request.POST.get('next', '')

        if state_name:
            new_state = State.objects.create(name=state_name)

            params = request.POST.copy()
            params['new_state'] = new_state.name
            params['show'] = 'state'
            query_string = urlencode(params)

        return redirect(f'/excise_details/{company_id}/?{query_string}')
    return redirect('/')


def service_tax_details(request, company_id):
    states = State.objects.all()
    company = get_object_or_404(Company, id=company_id)
    service_tax_details = ServiceTaxDetails.objects.filter(company=company).first()

    if service_tax_details:
        if service_tax_details.organisation_type:
            service_tax_details.organisation_type = service_tax_details.organisation_type.strip()

        print('DEBUG service_tax_details:', service_tax_details)
        print('  Registration Number:', service_tax_details.registration_number)
        print('  Organisation Type:', service_tax_details.organisation_type)
        print('  Set/Alter Service Tax:', service_tax_details.set_alter_service_tax)
        print('  Define Service Category Masters:', service_tax_details.define_service_category_masters)
        print('  Reverse Charge Applicable:', service_tax_details.reverse_charge_applicable)
        print('  Deactivate From:', service_tax_details.deactivate_from)
    next_page = request.GET.get('next')


    return render(request, 'company/service_tax_details.html', {
        'states': states,'company_id': company_id,'service_tax_details': service_tax_details,'next': next_page, 
    })



def service_tax_rate(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    service_tax_rate = ServiceTaxRate.objects.filter(company=company).first()
    next_page = request.GET.get('next')

    referer = request.META.get('HTTP_REFERER', '')
    from_next = ''
    if referer:
        parsed = urlparse(referer)
        query = parse_qs(parsed.query)
        if query.get('next', [None])[0] == 'alter':
            from_next = 'alter'



    return render(request, 'company/service_tax_rate.html', {
        'company_id': company_id,'company': company,'service_tax_rate': service_tax_rate,'next': next_page,'from_next': from_next,
    })


def payroll_statutory_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    payroll_details = PayrollStatutoryDetails.objects.filter(company=company).first()
    next_page = request.GET.get('next')

    return render(request, 'company/payroll_statutory_details.html', {
        'company_id': company_id,'company': company,'payroll_details': payroll_details,'next': next_page, 
    })


def merchant_profile_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    merchant_details = MerchantProfile.objects.filter(company=company).first()
    next_page = request.GET.get('next')

    return render(request, 'company/merchant_profile_details.html', {
        'company_id': company_id,'company': company,'merchant_details': merchant_details,'next': next_page, 
    })


def multiple_address_list(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    addresses = CompanyAddress.objects.filter(company=company)
    next_page = request.GET.get('next')

    primary_address = {
        'mailing_name': company.mailing_name,
        'address': company.address,
        'pincode': company.pincode,
        'telephone': company.telephone,
        'mobile':company.mobile,
        'country': company.fax,
        'email':company.email,
        'website':company.website
    }

    return render(request, 'company/multiple_address_list.html', {
        'company_id': company.id,'company': company,'addresses': addresses,'primary_address': primary_address,'next': next_page, 
    })


def create_multiple_address(request, company_id):
    next_page = request.GET.get('next') 
    company = get_object_or_404(Company, id=company_id)
    return render( request,'company/create_multiple_address.html',{'company_id': company_id,'next': next_page,'company':company})


def gst_rate_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    gst_rate_details = GSTRateDetails.objects.filter(company=company).first()
    next_page = request.GET.get('next')
    classification_list = Classification.objects.all()
    return render(request, 'company/gst_rate_details.html', {
        'company_id': company_id,'gst_rate_details': gst_rate_details,'next': next_page,'classification_list':classification_list 
    })




def create_company_fun(request):
    if request.method == 'POST':
        company_name = request.POST.get('company_name')
        mailing_name = request.POST.get('mailing_name')
        address = request.POST.get('address')
        state_name = request.POST.get('state')
        country_name = request.POST.get('country')
        pincode = request.POST.get('pincode')
        telephone = request.POST.get('telephone')
        mobile = request.POST.get('mobile')
        fax = request.POST.get('fax')
        email = request.POST.get('email')
        website = request.POST.get('website')
        financial_year = request.POST.get('financial_year')
        books_beginning = request.POST.get('books_beginning')
        currency_symbol = request.POST.get('currency_symbol')
        formal_name = request.POST.get('formal_name')

        state_obj = None
        if state_name:
            state_obj = State.objects.filter(name=state_name).first()

        country_obj = None
        if country_name:
            country_obj = Country.objects.filter(name=country_name).first()

        Company.objects.create(
            user=request.user, 
            name=company_name,
            mailing_name=mailing_name,
            address=address,
            state=state_obj,
            country=country_obj,
            pincode=pincode,
            telephone=telephone,
            mobile=mobile,
            fax=fax,
            email=email,
            website=website,
            financial_year_start=financial_year,
            books_start_date=books_beginning,
            base_currency_symbol=currency_symbol,
            formal_name=formal_name
        )

        return redirect('company_features')

    return render(request, 'create_company.html')



def create_gst_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    next_page = request.POST.get('next') 

    def to_bool(value):
        return value.strip().lower() == 'yes' if value else False

    if request.method == 'POST':
        state_name = request.POST.get('state')
        state = State.objects.filter(name=state_name).first()

        existing_gst = GSTDetails.objects.filter(company=company).first()

        if existing_gst:
            existing_gst.state = state
            existing_gst.registration_type = request.POST.get('registration_type')
            existing_gst.assessee_of_other_territory = to_bool(request.POST.get('assessee_of_other_territory'))
            existing_gst.gstin_uin = request.POST.get('gstin_uin')
            existing_gst.periodicity_gstr1 = request.POST.get('periodicity_gstr1')
            existing_gst.kerala_flood_cess = to_bool(request.POST.get('kerala_flood_cess'))
            existing_gst.gst_username = request.POST.get('gst_username')
            existing_gst.mode_of_filing = request.POST.get('mode_of_filing')
            existing_gst.einvoice_applicable = to_bool(request.POST.get('einvoice_applicable'))
            existing_gst.einvoice_applicable_from = request.POST.get('einvoice_applicable_from') or None
            existing_gst.invoice_bill_from_place = request.POST.get('invoice_bill_from_place')
            existing_gst.ewaybill_applicable = to_bool(request.POST.get('ewaybill_applicable'))
            existing_gst.ewaybill_applicable_from = request.POST.get('ewaybill_applicable_from') or None
            existing_gst.ewaybill_interstate = to_bool(request.POST.get('ewaybill_interstate'))
            existing_gst.create_another_registration = to_bool(request.POST.get('create_another_registration'))

            existing_gst.save()

        else:
            GSTDetails.objects.create(
                company=company,
                state=state,
                registration_type=request.POST.get('registration_type'),
                assessee_of_other_territory=to_bool(request.POST.get('assessee_of_other_territory')),
                gstin_uin=request.POST.get('gstin_uin'),
                periodicity_gstr1=request.POST.get('periodicity_gstr1'),
                kerala_flood_cess=to_bool(request.POST.get('kerala_flood_cess')),
                gst_username=request.POST.get('gst_username'),
                mode_of_filing=request.POST.get('mode_of_filing'),
                einvoice_applicable=to_bool(request.POST.get('einvoice_applicable')),
                einvoice_applicable_from=request.POST.get('einvoice_applicable_from') or None,
                invoice_bill_from_place=request.POST.get('invoice_bill_from_place'),
                ewaybill_applicable=to_bool(request.POST.get('ewaybill_applicable')),
                ewaybill_applicable_from=request.POST.get('ewaybill_applicable_from') or None,
                ewaybill_interstate=to_bool(request.POST.get('ewaybill_interstate')),
                create_another_registration=to_bool(request.POST.get('create_another_registration'))
            )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('company_features')

    return render(request, 'company/gst_details.html', {
        'company_id': company_id
    })



def create_gst_rate_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    next_page = request.POST.get('next')

    def to_bool(value):
        return value.strip().lower() == 'yes' if value else False

    if request.method == 'POST':
        # Retrieve all fields from POST data
        hsn_sac_details = request.POST.get('hsn_sac_details')
        hsn_sac = request.POST.get('hsn_sac')
        description = request.POST.get('description')
        classification_hsn = request.POST.get('classification_hsn')

        gst_rate_details_choice = request.POST.get('gst_rate_details_choice')
        taxability_type = request.POST.get('taxability_type')
        classification_gst = request.POST.get('classification_gst')
        gst_rate = request.POST.get('gst_rate') or 0

        interstate_threshold = request.POST.get('interstate_threshold')
        intrastate_threshold = request.POST.get('intrastate_threshold')
        threshold_includes = request.POST.get('threshold_includes')

        create_summary_for = request.POST.get('create_summary_for')
        minimum_length = request.POST.get('minimum_length') or None
        show_gst_advances = to_bool(request.POST.get('show_gst_advances'))
        application_from = request.POST.get('application_from')

        update_gst_status_vouchers = to_bool(request.POST.get('update_gst_status_vouchers'))
        update_gst_status_returns = to_bool(request.POST.get('update_gst_status_returns'))

        # Save or update
        obj, created = GSTRateDetails.objects.get_or_create(company=company)
        obj.hsn_sac_details = hsn_sac_details
        obj.hsn_sac = hsn_sac
        obj.description = description
        obj.classification_hsn = classification_hsn

        obj.gst_rate_details_choice = gst_rate_details_choice
        obj.taxability_type = taxability_type
        obj.classification_gst = classification_gst
        obj.gst_rate = gst_rate

        obj.interstate_threshold = interstate_threshold
        obj.intrastate_threshold = intrastate_threshold
        obj.threshold_includes = threshold_includes

        obj.create_summary_for = create_summary_for
        obj.minimum_length = minimum_length
        obj.show_gst_advances = show_gst_advances
        obj.application_from = application_from

        obj.update_gst_status_vouchers = update_gst_status_vouchers
        obj.update_gst_status_returns = update_gst_status_returns

        obj.save()

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        return redirect('company_features')

    return render(request, 'company/gst_rate_details.html', {
        'company_id': company_id
    })


def create_tds_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    existing_tds = TDSDeductorDetails.objects.filter(company=company).first()
    next_page = request.POST.get('next')

    def to_bool(value):
        return value.strip().lower() == 'yes' if value else False

    if request.method == 'POST':
        if existing_tds:
            existing_tds.tan_registration_number = request.POST.get('tan_registration_number')
            existing_tds.tan = request.POST.get('tan')
            existing_tds.deductor_type = request.POST.get('deductor_type')
            existing_tds.deductor_branch = request.POST.get('deductor_branch')
            existing_tds.alter_person_responsible = to_bool(request.POST.get('alter_person_responsible'))
            existing_tds.ignore_it_exemption_limit = to_bool(request.POST.get('ignore_it_exemption_limit'))
            existing_tds.activate_tds_stock_item = to_bool(request.POST.get('activate_tds_stock_item'))
            existing_tds.save()
        else:
            TDSDeductorDetails.objects.create(
                company=company,
                tan_registration_number=request.POST.get('tan_registration_number'),
                tan=request.POST.get('tan'),
                deductor_type=request.POST.get('deductor_type'),
                deductor_branch=request.POST.get('deductor_branch'),
                alter_person_responsible=to_bool(request.POST.get('alter_person_responsible')),
                ignore_it_exemption_limit=to_bool(request.POST.get('ignore_it_exemption_limit')),
                activate_tds_stock_item=to_bool(request.POST.get('activate_tds_stock_item')),
            )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('company_features')


    return render(request, 'company/company_tds_details.html', {
        'company_id': company_id,
        'tds_details': existing_tds
    })





def create_tcs_collector_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    tcs_details = TCSCollectorDetails.objects.filter(company=company).first()
    next_page = request.POST.get('next')

    def to_bool(value):
        return value.strip().lower() == 'yes' if value else False

    if request.method == 'POST':
        if tcs_details:
            tcs_details.tan_registration_number = request.POST.get('tan_registration_number')
            tcs_details.tax_eduction_collection_account_number = request.POST.get('tan')
            tcs_details.collector_type = request.POST.get('collector_type')
            tcs_details.collector_branch = request.POST.get('collector_branch')
            tcs_details.alter_person_responsible = to_bool(request.POST.get('alter_person_responsible'))
            tcs_details.ignore_it_exemption_limit = to_bool(request.POST.get('ignore_it_exemption_limit'))
            tcs_details.save()
        else:
            TCSCollectorDetails.objects.create(
                company=company,
                tan_registration_number=request.POST.get('tan_registration_number'),
                tax_eduction_collection_account_number=request.POST.get('tan'),
                collector_type=request.POST.get('collector_type'),
                collector_branch=request.POST.get('collector_branch'),
                alter_person_responsible=to_bool(request.POST.get('alter_person_responsible')),
                ignore_it_exemption_limit=to_bool(request.POST.get('ignore_it_exemption_limit')),
            )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('company_features')

    return render(request, 'company/company_tcs_details.html', {
        'company_id': company_id,
        'tcs_details': tcs_details
    })



def create_vat_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    vat_details = VATDetails.objects.filter(company=company).first()

    if request.method == 'POST':
        next_page = request.GET.get('next') or request.POST.get('next') or ''
        print(f"DEBUG POST next_page={next_page}")

        def to_bool(value):
            return value.strip().lower() == 'yes' if value else False

        state_name = request.POST.get('state')
        state = State.objects.filter(name=state_name).first()

        if vat_details:
            vat_details.state = state
            vat_details.tin = request.POST.get('tin')
            vat_details.interstate_sales_tax_number = request.POST.get('interstate_sales_tax_number')
            vat_details.alter_tax_rate_details = to_bool(request.POST.get('alter_tax_rate_details'))
            vat_details.define_vat_commodity = to_bool(request.POST.get('define_vat_commodity'))
            vat_details.deactivate_from = request.POST.get('deactivate_from') or None
            vat_details.save()
        else:
            VATDetails.objects.create(
                company=company,
                state=state,
                tin=request.POST.get('tin'),
                interstate_sales_tax_number=request.POST.get('interstate_sales_tax_number'),
                alter_tax_rate_details=to_bool(request.POST.get('alter_tax_rate_details')),
                define_vat_commodity=to_bool(request.POST.get('define_vat_commodity')),
                deactivate_from=request.POST.get('deactivate_from') or None
            )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('company_features')

    else:
        next_page = request.GET.get('next') 
        print(f"DEBUG: Inside GET request. next_page value: {next_page}")

        states = State.objects.all()

        return render(request, 'company/vat_details.html', {
            'company_id': company_id,
            'states': states,
            'vat_details': vat_details,
            'next': next_page
        })




def create_excise_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    excise_details = ExciseDetails.objects.filter(company=company).first()

    if request.method == 'POST':
        next_page = request.POST.get('next')
        print(f"DEBUG: Inside POST request. next_page value: {next_page}")

        def to_bool(value):
            return value.strip().lower() == 'yes' if value else False

        state_name = request.POST.get('state')
        state = State.objects.filter(name=state_name).first()

        if excise_details:
            excise_details.state = state
            excise_details.unit_name = request.POST.get('unit_name')
            excise_details.address = request.POST.get('address')
            excise_details.pincode = request.POST.get('pincode')
            excise_details.telephone_number = request.POST.get('telephone_number')
            excise_details.registration_type = request.POST.get('registration_type')
            excise_details.type_of_manufacturer = request.POST.get('type_of_manufacturer')
            excise_details.ecc_number = request.POST.get('ecc_number')
            excise_details.set_alter_tariff = to_bool(request.POST.get('set_alter_tariff'))
            excise_details.define_tariff_masters = to_bool(request.POST.get('define_tariff_masters'))
            excise_details.deactivate_from = request.POST.get('deactivate_from') or None
            excise_details.save()
        else:
            ExciseDetails.objects.create(
                company=company,
                state=state,
                unit_name=request.POST.get('unit_name'),
                address=request.POST.get('address'),
                pincode=request.POST.get('pincode'),
                telephone_number=request.POST.get('telephone_number'),
                registration_type=request.POST.get('registration_type'),
                type_of_manufacturer=request.POST.get('type_of_manufacturer'),
                ecc_number=request.POST.get('ecc_number'),
                set_alter_tariff=to_bool(request.POST.get('set_alter_tariff')),
                define_tariff_masters=to_bool(request.POST.get('define_tariff_masters')),
                deactivate_from=request.POST.get('deactivate_from') or None
            )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('company_features')

    else:
        next_page = request.GET.get('next')
        print(f"DEBUG: Inside GET request. next_page value: {next_page}")

        states = State.objects.all()

        return render(request, 'company/excise_details.html', {
            'company_id': company_id,
            'states': states,
            'excise_details': excise_details,
            'next': next_page
        })



def create_service_tax_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    service_tax_details = ServiceTaxDetails.objects.filter(company=company).first()

    if request.method == 'POST':
        next_page = request.POST.get('next')
        print(f"DEBUG: Inside POST. next_page = {next_page}")

        def to_bool(value):
            return value.strip().lower() == 'yes' if value else False

        if service_tax_details:
            service_tax_details.registration_number = request.POST.get('registration_number')
            service_tax_details.organisation_type = request.POST.get('organisation_type')
            service_tax_details.set_alter_service_tax = to_bool(request.POST.get('set_alter_service_tax'))
            service_tax_details.define_service_category_masters = to_bool(request.POST.get('define_service_category_masters'))
            service_tax_details.reverse_charge_applicable = to_bool(request.POST.get('reverse_charge_applicable'))
            service_tax_details.deactivate_from = request.POST.get('deactivate_from') or None
            service_tax_details.is_monthly_format = to_bool(request.POST.get('is_monthly_format'))
            service_tax_details.compute_tax_liability = request.POST.get('compute_tax_liability')
            service_tax_details.save()
        else:
            ServiceTaxDetails.objects.create(
                company=company,
                registration_number=request.POST.get('registration_number'),
                organisation_type=request.POST.get('organisation_type'),
                set_alter_service_tax=to_bool(request.POST.get('set_alter_service_tax')),
                define_service_category_masters=to_bool(request.POST.get('define_service_category_masters')),
                reverse_charge_applicable=to_bool(request.POST.get('reverse_charge_applicable')),
                deactivate_from=request.POST.get('deactivate_from') or None,
                is_monthly_format=to_bool(request.POST.get('is_monthly_format')),
                compute_tax_liability=request.POST.get('compute_tax_liability')
            )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('company_features')

    else:
        next_page = request.GET.get('next')
        print(f"DEBUG: Inside GET. next_page = {next_page}")

        return render(request, 'company/service_tax_details.html', {
            'company_id': company_id,
            'service_tax_details': service_tax_details,
            'next': next_page
        })




def create_service_tax_rate_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    rate_name = request.GET.get('name') or request.POST.get('name')

    service_tax_rate = None
    if rate_name:
        service_tax_rate = ServiceTaxRate.objects.filter(company=company, name=rate_name).first()

    if request.method == 'POST':
        if service_tax_rate:
            service_tax_rate.service_tax = request.POST.get('service_tax') or 0
            service_tax_rate.education_cess = request.POST.get('education_cess') or 0
            service_tax_rate.secondary_education_cess = request.POST.get('secondary_education_cess') or 0
            service_tax_rate.swachh_bharat_cess = request.POST.get('swachh_bharat_cess') or 0
            service_tax_rate.krishi_kalyan_cess = request.POST.get('krishi_kalyan_cess') or 0
            service_tax_rate.save()
        else:
            ServiceTaxRate.objects.create(
                company=company,
                name=request.POST.get('name'),
                service_tax=request.POST.get('service_tax') or 0,
                education_cess=request.POST.get('education_cess') or 0,
                secondary_education_cess=request.POST.get('secondary_education_cess') or 0,
                swachh_bharat_cess=request.POST.get('swachh_bharat_cess') or 0,
                krishi_kalyan_cess=request.POST.get('krishi_kalyan_cess') or 0
            )

        return redirect(f'/service_tax_details/{company.id}/?from=rate')

    return render(request, 'company/service_tax_rate.html', {
        'company': company,
        'service_tax_rate': service_tax_rate
    })


def create_payroll_statutory_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    payroll_details = PayrollStatutoryDetails.objects.filter(company=company).first()

    if request.method == 'POST':
        next_page = request.POST.get('next')
        print(f"DEBUG: Inside POST. next_page = {next_page}")

        if payroll_details:
            payroll_details.pf_company_code = request.POST.get('pf_company_code')
            payroll_details.pf_account_group_code = request.POST.get('pf_account_group_code')
            payroll_details.pf_security_code = request.POST.get('pf_security_code')
            payroll_details.esi_company_code = request.POST.get('esi_company_code')
            payroll_details.esi_branch_office = request.POST.get('esi_branch_office')
            payroll_details.esi_working_days = request.POST.get('esi_working_days') or None
            payroll_details.nps_registration_number = request.POST.get('nps_registration_number')
            payroll_details.nps_branch_office_number = request.POST.get('nps_branch_office_number')
            payroll_details.tan = request.POST.get('tan')
            payroll_details.tan_registration_number = request.POST.get('tan_registration_number')
            payroll_details.income_class_circle = request.POST.get('income_class_circle')
            payroll_details.deductor_type = request.POST.get('deductor_type')
            payroll_details.deductor_branch = request.POST.get('deductor_branch')
            payroll_details.person_responsible = request.POST.get('person_responsible')
            payroll_details.son_daughter_of = request.POST.get('son_daughter_of')
            payroll_details.designation = request.POST.get('designation')
            payroll_details.pan = request.POST.get('pan')
            payroll_details.save()
        else:
            PayrollStatutoryDetails.objects.create(
                company=company,
                pf_company_code=request.POST.get('pf_company_code'),
                pf_account_group_code=request.POST.get('pf_account_group_code'),
                pf_security_code=request.POST.get('pf_security_code'),
                esi_company_code=request.POST.get('esi_company_code'),
                esi_branch_office=request.POST.get('esi_branch_office'),
                esi_working_days=request.POST.get('esi_working_days') or None,
                nps_registration_number=request.POST.get('nps_registration_number'),
                nps_branch_office_number=request.POST.get('nps_branch_office_number'),
                tan=request.POST.get('tan'),
                tan_registration_number=request.POST.get('tan_registration_number'),
                income_class_circle=request.POST.get('income_class_circle'),
                deductor_type=request.POST.get('deductor_type'),
                deductor_branch=request.POST.get('deductor_branch'),
                person_responsible=request.POST.get('person_responsible'),
                son_daughter_of=request.POST.get('son_daughter_of'),
                designation=request.POST.get('designation'),
                pan=request.POST.get('pan')
            )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('company_features')

    else:
        next_page = request.GET.get('next')
        print(f"DEBUG: Inside GET. next_page = {next_page}")

        return render(request, 'company/payroll_statutory_details.html', {
            'company_id': company_id,
            'payroll_details': payroll_details,
            'next': next_page
        })


def create_merchant_profile(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    merchant_profile = MerchantProfile.objects.filter(company=company).first()

    if request.method == 'POST':
        next_page = request.POST.get('next')
        print(f"DEBUG: Inside POST. next_page = {next_page}")

        name = request.POST.get('name')
        payment_method = request.POST.get('payment_method')
        merchant_name = request.POST.get('merchant_name')
        create_another = request.POST.get('create_another') == 'Yes'
        merchant_id = request.POST.get('merchant_id')
        registered_email = request.POST.get('registered_email')
        upi_id = request.POST.get('upi_id')

        if merchant_profile:
            merchant_profile.name = name
            merchant_profile.payment_method = payment_method
            merchant_profile.merchant_name = merchant_name
            merchant_profile.create_another = create_another
            merchant_profile.merchant_id = merchant_id
            merchant_profile.registered_email = registered_email
            merchant_profile.upi_id = upi_id
            merchant_profile.save()
        else:
            MerchantProfile.objects.create(
                company=company,
                name=name,
                payment_method=payment_method,
                merchant_name=merchant_name,
                create_another=create_another,
                merchant_id=merchant_id,
                registered_email=registered_email,
                upi_id=upi_id
            )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('company_features')

    else:
        next_page = request.GET.get('next')
        print(f"DEBUG: Inside GET. next_page = {next_page}")

        return render(request, 'company/merchant_profile_details.html', {
            'company_id': company_id,
            'company': company,
            'merchant_profile': merchant_profile,
            'next': next_page
        })



def create_multiple_company_address(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    if request.method == 'POST':
        next_page = request.POST.get('next')

        CompanyAddress.objects.create(
            company=company,
            mailing_name=request.POST.get('mailing_name'),
            address=request.POST.get('address'),
            pincode=request.POST.get('pincode'),
            phone=request.POST.get('phone'),
            mobile=request.POST.get('mobile'),
            fax=request.POST.get('fax'),
            email=request.POST.get('email'),
            website=request.POST.get('website')
        )

        if next_page == 'alter':
            return redirect(f"{reverse('alter_company_features')}?company_id={company.id}")
        else:
            return redirect('multiple_address_list', company_id=company.id)

    else:
        next_page = request.GET.get('next')

    return render(request, 'company/create_address.html', {
        'company_id': company.id,
        'next': next_page,
    })



def save_company_features(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        company = get_object_or_404(Company, id=company_id)

        features, created = CompanyFeatures.objects.get_or_create(company=company)

        boolean_fields = [
            'maintain_accounts',
            'enable_bill_wise_entry',
            'enable_cost_centres',
            'enable_interest_calculations',
            'maintain_inventory',
            'integrate_accounts_inventory',
            'enable_multiple_price_levels',
            'enable_batches',
            'maintain_expiry_for_batches',
            'enable_job_order_processing',
            'enable_cost_tracking',
            'enable_job_costing',
            'use_discount_column',
            'use_actual_billed_qty_columns',
            'enable_gst',
            'alter_gst_details',
            'enable_tds',
            'enable_tcs',
            'enable_vat',
            'enable_excise',
            'enable_service_tax',
            'enable_browser_access',
            'enable_remote_access',
            'maintain_payroll',
            'enable_payroll_statutory',
            'enable_payment_request',
            'enable_multiple_address',
            'mark_modified_vouchers',
        ]

        for field in boolean_fields:
            value = request.POST.get(field, "No")
            setattr(features, field, value.lower() == 'yes')

        features.save()
        return redirect('userDashboard')
    
    return redirect('userDashboard')


def dashboard(request):
    return render(request,'dashboard.html')


def save_date_range(request):
    if request.method == 'POST':
        date_range = request.POST.get('date_range')
        obj, created = DateRange.objects.get_or_create(
            user=request.user,
            defaults={'date_range': date_range}
        )
        if not created:
            obj.date_range = date_range
            obj.save()

        return redirect('userDashboard')
    return render(request, 'user_dashboard.html')


def save_current_date(request):
    if request.method == 'POST':
        current_date = request.POST.get('current_date')
        obj, created = CurrentDate.objects.get_or_create(
            user=request.user,
            defaults={'current_date': current_date}
        )
        if not created:
            obj.current_date = current_date
            obj.save()

        return redirect('userDashboard')
    return render(request, 'user_dashboard.html')


def alter_company(request):
    states = State.objects.all()
    countries = Country.objects.all()
    show = request.GET.get('show', '')
    user_companies = Company.objects.filter(user=request.user)

    selected_company_id = request.GET.get('company_id')
    selected_company = None

    if selected_company_id:
        try:
            selected_company = user_companies.get(id=selected_company_id)
        except Company.DoesNotExist:
            selected_company = None
    elif user_companies.exists():
        selected_company = user_companies.first()

    context = {
        'companies': user_companies,
        'selected_company': selected_company,
        'states': states,
        'countries': countries,
        'show': show
    }

    return render(request, 'company/alter_company.html', context)


def create_new_state_alter(request):
    if request.method == 'POST':
        state = request.POST.get('state')
        if state:
            State.objects.create(name=state)
    return redirect('/alter_company/?show=state')


def create_new_country_alter(request):
    if request.method == 'POST':
        country = request.POST.get('country')
        if country:
            Country.objects.create(name=country)
    return redirect('/alter_company/?show=country')





def alter_company_fun(request, company_id):
    company = get_object_or_404(Company, id=company_id, user=request.user)

    if request.method == 'POST':
        company.name = request.POST['name']
        company.mailing_name = request.POST['mailing_name']
        company.address = request.POST['address']
        
        state_name = request.POST['state']
        try:
            company.state = State.objects.get(name=state_name)
        except State.DoesNotExist:
            company.state = None  

        country_name = request.POST['country']
        try:
            company.country = Country.objects.get(name=country_name)
        except Country.DoesNotExist:
            company.country = None 

        company.pincode = request.POST['pincode']
        company.telephone = request.POST['telephone']
        company.mobile = request.POST['mobile']
        company.fax = request.POST['fax']
        company.email = request.POST['email']
        company.website = request.POST['website']
        company.financial_year_start = request.POST['financial_year']
        company.books_start_date = request.POST['books_beginning']
        company.base_currency_symbol = request.POST['currency_symbol']
        company.formal_name = request.POST['formal_name']
        company.save()

        return redirect(f'/alter_company?company_id={company.id}')

    return redirect('alter_company')



def change_company(request):
    user_companies = Company.objects.filter(user=request.user).order_by('-id')

    unlocked_ids = request.session.get('vault_authenticated_company_ids', [])
    vault_protected_ids = set(
        Company.objects.filter(
            user=request.user,
            tallyvaultsetting__isnull=False
        ).values_list('id', flat=True)
    )

    companies = []
    for c in user_companies:
        if c.id in vault_protected_ids and c.id not in unlocked_ids:
            name = '**********'
        else:
            name = c.name
        companies.append({'id': c.id, 'name': name})

    return render(request, 'company/change_company.html', {'companies': companies})



def select_company(request):
    user_companies = Company.objects.filter(user=request.user).order_by('-id')
    unlocked_ids = request.session.get('vault_authenticated_company_ids', [])
    vault_protected_ids = set(
        Company.objects.filter(
            user=request.user,
            tallyvaultsetting__isnull=False
        ).values_list('id', flat=True)
    )

    companies = []
    for c in user_companies:
        if c.id in vault_protected_ids and c.id not in unlocked_ids:
            name = '**********'
        else:
            name = c.name
        companies.append({'id': c.id, 'name': name})

    return render(request,'company/select_company.html', {'companies': companies})


def tally_netuser(request):
    return render(request,'company/tally_netuser.html')


def shut_company(request):
    user_companies = Company.objects.filter(user=request.user).order_by('-id')
    unlocked_ids = request.session.get('vault_authenticated_company_ids', [])
    vault_protected_ids = set(
        Company.objects.filter(
            user=request.user,
            tallyvaultsetting__isnull=False
        ).values_list('id', flat=True)
    )

    companies = []
    for c in user_companies:
        if c.id in vault_protected_ids and c.id not in unlocked_ids:
            name = '**********'
        else:
            name = c.name
        companies.append({'id': c.id, 'name': name})

    return render(request,'company/shut_company.html', {'companies': companies})



def security_user_access(request):
    user_companies = Company.objects.filter(user=request.user).order_by('name')
    all_users = NewUsers.objects.all()
    unlocked_ids = request.session.get('vault_authenticated_company_ids', [])
    vault_protected_ids = set(
        Company.objects.filter(
            user=request.user,
            tallyvaultsetting__isnull=False
        ).values_list('id', flat=True)
    )

    companies = []
    for c in user_companies:
        if c.id in vault_protected_ids and c.id not in unlocked_ids:
            name = '**********'
        else:
            name = c.name
        companies.append({'id': c.id, 'name': name})

    return render(request, 'company/security_user_access.html', {'companies': companies,'all_users':all_users})


def tally_vault(request):
    user_companies = Company.objects.filter(user=request.user).order_by('name')
    unlocked_ids = request.session.get('vault_authenticated_company_ids', [])
    vault_protected_ids = set(
        Company.objects.filter(
            user=request.user,
            tallyvaultsetting__isnull=False
        ).values_list('id', flat=True)
    )

    companies = []
    for c in user_companies:
        if c.id in vault_protected_ids and c.id not in unlocked_ids:
            name = '**********'
        else:
            name = c.name
        companies.append({'id': c.id, 'name': name})

    return render(request,'company/tally_vault.html', {'companies': companies,})





def create_tally_vault_setting(request):
    companies = Company.objects.all()  

    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if not company_id or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('tally_vault')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('tally_vault')

        hashed_password = make_password(password)

        company = get_object_or_404(Company, id=company_id)

        TallyVaultSetting.objects.update_or_create(
            company=company,
            defaults={
                'vault_password': hashed_password,
                'user': request.user,
            }
        )

        request.session['vault_force_check'] = True
        return redirect('userDashboard')

    return render(request, 'company/create_tally_vault.html', {'companies': companies})




def verify_tally_vault_password(request):
    if request.method == "POST":
        entered_password = request.POST.get("vault_password")
        
        if not entered_password:
            return JsonResponse({"success": False, "error": "Please enter a password."})

        vault_entries = TallyVaultSetting.objects.filter(user=request.user)
        matching_company_ids = []

        for vault in vault_entries:
            if check_password(entered_password, vault.vault_password):
                matching_company_ids.append(vault.company.id)

        if matching_company_ids:
            unlocked = request.session.get('vault_authenticated_company_ids', [])
            unlocked = list(set(unlocked + matching_company_ids))
            request.session['vault_authenticated_company_ids'] = unlocked
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Incorrect vault password."})
    
    return JsonResponse({"success": False, "error": "Invalid request."})



def alter_company_features(request):
    user_companies = Company.objects.filter(user=request.user).order_by('-id')
    selected_company_id = request.GET.get('company_id')
    selected_company = None
    company_features = None

    if selected_company_id:
        try:
            selected_company = user_companies.get(id=selected_company_id)
            company_features = CompanyFeatures.objects.filter(company=selected_company).first()
        except Company.DoesNotExist:
            selected_company = None

    context = {
        'companies': user_companies,
        'selected_company': selected_company,
        'company_features': company_features,
    }
    return render(request, 'company/alter_company_features.html', context)



def update_company_features(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        company = get_object_or_404(Company, id=company_id)

        try:
            features = CompanyFeatures.objects.get(company=company)
        except CompanyFeatures.DoesNotExist:
            return redirect('alter_company_features')

        boolean_fields = [
            'maintain_accounts',
            'enable_bill_wise_entry',
            'enable_cost_centres',
            'enable_interest_calculations',
            'maintain_inventory',
            'integrate_accounts_inventory',
            'enable_multiple_price_levels',
            'enable_batches',
            'maintain_expiry_for_batches',
            'enable_job_order_processing',
            'enable_cost_tracking',
            'enable_job_costing',
            'use_discount_column',
            'use_actual_billed_qty_columns',
            'enable_gst',
            'alter_gst_details',
            'enable_tds',
            'enable_tcs',
            'enable_vat',
            'enable_excise',
            'enable_service_tax',
            'enable_browser_access',
            'enable_remote_access',
            'maintain_payroll',
            'enable_payroll_statutory',
            'enable_payment_request',
            'enable_multiple_address',
            'mark_modified_vouchers',
        ]

        for field in boolean_fields:
            value = request.POST.get(field, "No")
            setattr(features, field, value.lower() == 'yes')

        features.save()

        if not features.enable_gst:
            GSTDetails.objects.filter(company=company).delete()

        if not features.alter_gst_details:
            GSTRateDetails.objects.filter(company=company).delete()

        if not features.enable_tds:
            TDSDeductorDetails.objects.filter(company=company).delete()

        if not features.enable_tcs:
            TCSCollectorDetails.objects.filter(company=company).delete()

        if not features.enable_service_tax:
            ServiceTaxRate.objects.filter(company=company).delete()

        if not features.maintain_payroll:
            PayrollStatutoryDetails.objects.filter(company=company).delete()

        if not features.enable_payment_request:
            MerchantProfile.objects.filter(company=company).delete()

        if not features.enable_multiple_address:
            CompanyAddress.objects.filter(company=company).delete()

        if not features.enable_vat:
            VATDetails.objects.filter(company=company).delete()

        if not features.enable_excise:
            ExciseDetails.objects.filter(company=company).delete()

        return redirect('userDashboard')

    return redirect('userDashboard')



def LogOut(request):
    auth.logout(request)
    return redirect('index')




def set_default_states_and_countries():
    state_names = [
        "Andaman and Nicobar Islands",
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chhattisgarh",
        "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jammu and Kashmir",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Ladakh",
        "Lakshadweep",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Puducherry",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttarakhand",
        "Uttar Pradesh",
        "West Bengal"
    ]

    country_names = [
        "Bangladesh",
        "Bhutan",
        "Botswana",
        "Egypt",
        "Ghana",
        "Hong Kong",
        "India",
        "Indonesia",
        "Kenya",
        "Kingdom of Bahrain",
        "Kuwait",
        "Liberia",
        "Malawi",
        "Malaysia",
        "Myanmar",
        "Nepal",
        "Nigeria",
        "Philippines",
        "Qatar",
        "Saudi Arabia",
        "Singapore",
        "South Africa",
        "Sri Lanka",
        "Sultanate of Oman",
        "Tanzania",
        "Thailand",
        "UAE",
        "Uganda",
        "UK",
        "United States of America",
        "Zambia",
    ]

    if not State.objects.exists():
        for name in state_names:
            State.objects.create(name=name.strip())

    if not Country.objects.exists():
        for name in country_names:
            Country.objects.create(name=name.strip())


#SECOND WORK

def update_effective_date(request):
    if request.method == 'POST':
        effective_date = request.POST.get('effective_date')
        if effective_date:
            CurrentDate.objects.update_or_create(
                user=request.user,
                defaults={'current_date': effective_date}
            )
        return redirect('gst_details', company_id=request.POST.get('company_id'))
    else:
        return redirect('gst_details',company_id=request.POST.get('company_id'))
    


def gst_effective_date(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    effective_dates = GSTEffectiveDate.objects.all()
    return render(request, 'company/gst_effective_date.html', {
        'company': company,
        'company_id': company_id,'effective_dates':effective_dates
    })


def save_effective_date(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        effective_date = request.POST.get('effective_date')

        company = get_object_or_404(Company, id=company_id)

        GSTEffectiveDate.objects.create(
            company=company,
            date=effective_date
        )
        company.save()

        return redirect('gst_effective_date', company_id=request.POST.get('company_id'))

    return redirect('gst_effective_date', company_id=request.POST.get('company_id'))



def gst_settings(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    saved_return_types = list(GSTSettings.objects.filter(company=company).values_list('return_type', flat=True))
    referer = request.META.get('HTTP_REFERER', '')
    from_next = ''
    if referer:
        parsed = urlparse(referer)
        query = parse_qs(parsed.query)
        if query.get('next', [None])[0] == 'alter':
            from_next = 'alter'

    return render(request, 'company/gst_settings.html', {
        'company_id': company_id,
        'saved_return_types': saved_return_types,'from_next': from_next,
    })


def save_gst_return_types(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        print(f"company_id:{company_id}")
        company = get_object_or_404(Company, id=company_id)
        selected_return_types = request.POST.getlist('return_types')

        GSTSettings.objects.filter(company=company).delete()

        for return_type in selected_return_types:
            GSTSettings.objects.create(
                company=company,
                return_type=return_type
            )

        return redirect('gst_rate_details', company_id=company_id)

    return redirect('gst_settings',  company_id=company_id)


def slab_based_tax_rate(request,company_id):
    company = get_object_or_404(Company, id=company_id)
    slabs = SlabRate.objects.filter(company=company)
    return render(request,'company/slab_based_tax_rate.html',{'company_id': company_id,'slabs': slabs})



def parse_decimal_or_none(value):
    try:
        return Decimal(value.strip()) if value and value.strip() else None
    except (InvalidOperation, AttributeError):
        return None

def save_slab_rates(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        company = get_object_or_404(Company, id=company_id)

        greater_than_list = request.POST.getlist('greater-than')
        rate_upto_list = request.POST.getlist('up-to')
        taxability_list = request.POST.getlist('taxability')
        gst_rate_list = request.POST.getlist('rate')
        slab_id_list = request.POST.getlist('slab_id')

        for i in range(len(greater_than_list)):
            greater_than = parse_decimal_or_none(greater_than_list[i])
            rate_upto = parse_decimal_or_none(rate_upto_list[i])
            taxability = taxability_list[i].strip() if i < len(taxability_list) else ''
            gst_rate_raw = gst_rate_list[i] if i < len(gst_rate_list) else ''
            gst_rate_raw = gst_rate_raw.replace('%', '').strip()
            gst_rate = parse_decimal_or_none(gst_rate_raw)
            slab_id = slab_id_list[i] if i < len(slab_id_list) else ''

            if not (greater_than or rate_upto or taxability or gst_rate):
                continue

            if slab_id:
                try:
                    slab = SlabRate.objects.get(id=slab_id, company=company)
                    slab.greater_than = greater_than
                    slab.rate_upto = rate_upto
                    slab.taxability = taxability
                    slab.gst_rate = gst_rate
                    slab.save()
                except SlabRate.DoesNotExist:
                    pass  
            else:
                SlabRate.objects.create(
                    company=company,
                    greater_than=greater_than,
                    rate_upto=rate_upto,
                    taxability=taxability,
                    gst_rate=gst_rate
                )

        return redirect('slab_based_tax_rate', company_id=company_id)




def tds_person_responsible_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    states = State.objects.all()

    try:
        person = TDSPersonResponsibleDetail.objects.get(company=company)
    except TDSPersonResponsibleDetail.DoesNotExist:
        person = None

    get_data = request.GET or {}

    fields = ['name', 'parent_name', 'designation', 'pan', 'flat_no', 'building_name', 'road', 'area', 'town', 'pincode', 'mobile', 'std_code', 'telephone', 'email']

    data = {}
    for field in fields:
        value = get_data.get(field)
        if not value and person:
            value = getattr(person, field, '')

        if field == 'flat_no' and not value:
            value = f"{company.state.name}-{company.pincode},{company.country.name}"

        data[field] = value or ''

    referer = request.META.get('HTTP_REFERER', '')
    from_next = ''
    if referer:
        parsed = urlparse(referer)
        query = parse_qs(parsed.query)
        if query.get('next', [None])[0] == 'alter':
            from_next = 'alter'

    return render(request, 'company/tds_person_responsible_details.html', {
        'company_id': company_id,
        'company': company,
        'states': states,
        'person': person,
        'form_data': data, 'from_next': from_next,
    })



def tds_person_create_new_state(request):
    if request.method == 'POST':
        state_name = request.POST.get('state')
        if state_name:
            new_state = State.objects.create(name=state_name)
            
            params = request.POST.copy()
            params['new_state'] = new_state.name
            params['show'] = 'state'
            query_string = urlencode(params)
            return redirect(f'/tds_person_responsible_details/{request.POST.get("company_id")}/?{query_string}')
    return redirect('/') 




def save_tds_person_responsible_details(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        company = get_object_or_404(Company, id=company_id)

        person, created = TDSPersonResponsibleDetail.objects.get_or_create(company=company)
        person.name = request.POST.get('name')
        person.parent_name = request.POST.get('parent_name')
        person.designation = request.POST.get('designation')
        person.pan = request.POST.get('pan')
        person.flat_no = request.POST.get('flat_no')
        person.building_name = request.POST.get('building_name')
        person.road = request.POST.get('road')
        person.area = request.POST.get('area')
        person.town = request.POST.get('town')
        
        state_name = request.POST.get('state')
        if state_name:
            states = State.objects.filter(name=state_name)
            if states.exists():
                person.state = states.first()
            else:
                person.state = None
        else:
            person.state = None

        person.pincode = request.POST.get('pincode')
        person.mobile = request.POST.get('mobile')
        person.std_code = request.POST.get('std_code')
        person.telephone = request.POST.get('telephone')
        person.email = request.POST.get('email')

        person.save()

        return redirect('tds_person_responsible_details', company_id=company.id)

    company_id = request.GET.get('company_id')
    company = get_object_or_404(Company, id=company_id)
    person = TDSPersonResponsibleDetail.objects.filter(company=company).first()
    states = State.objects.all()

    return render(request, 'company/tds_person_responsible_details.html', {
        'company': company,
        'person': person,
        'states': states,
        'company_id': company_id,
    })



def tcs_person_responsible_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    states = State.objects.all()

    try:
        person = TCSPersonResponsibleDetail.objects.get(company=company)
    except TCSPersonResponsibleDetail.DoesNotExist:
        person = None

    get_data = request.GET or {}

    fields = ['name', 'parent_name', 'designation', 'pan', 'flat_no', 'building_name', 'road', 'area', 'town', 'pincode', 'mobile', 'std_code', 'telephone', 'email']

    data = {}
    for field in fields:
        value = get_data.get(field)
        if not value and person:
            value = getattr(person, field, '')

        if field == 'flat_no' and not value:
            value = f"{company.state.name}-{company.pincode},{company.country.name}"

        data[field] = value or ''
    
    referer = request.META.get('HTTP_REFERER', '')
    from_next = ''
    if referer:
        parsed = urlparse(referer)
        query = parse_qs(parsed.query)
        if query.get('next', [None])[0] == 'alter':
            from_next = 'alter'

    return render(request, 'company/tcs_person_responsible_details.html', {
        'company_id': company_id,
        'company': company,
        'states': states,
        'person': person,
        'form_data': data,'from_next': from_next,
    })



def tcs_person_create_new_state(request):
    if request.method == 'POST':
        state_name = request.POST.get('state')
        if state_name:
            new_state = State.objects.create(name=state_name)
            
            params = request.POST.copy()
            params['new_state'] = new_state.name
            params['show'] = 'state'
            query_string = urlencode(params)
            return redirect(f'/tcs_person_responsible_details/{request.POST.get("company_id")}/?{query_string}')
    return redirect('/') 




def save_tcs_person_responsible_details(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        company = get_object_or_404(Company, id=company_id)

        person, created = TCSPersonResponsibleDetail.objects.get_or_create(company=company)
        person.name = request.POST.get('name')
        person.parent_name = request.POST.get('parent_name')
        person.designation = request.POST.get('designation')
        person.pan = request.POST.get('pan')
        person.flat_no = request.POST.get('flat_no')
        person.building_name = request.POST.get('building_name')
        person.road = request.POST.get('road')
        person.area = request.POST.get('area')
        person.town = request.POST.get('town')
        
        state_name = request.POST.get('state')
        if state_name:
            states = State.objects.filter(name=state_name)
            if states.exists():
                person.state = states.first()
            else:
                person.state = None
        else:
            person.state = None

        person.pincode = request.POST.get('pincode')
        person.mobile = request.POST.get('mobile')
        person.std_code = request.POST.get('std_code')
        person.telephone = request.POST.get('telephone')
        person.email = request.POST.get('email')

        person.save()

        return redirect('tcs_person_responsible_details', company_id=company.id)

    company_id = request.GET.get('company_id')
    company = get_object_or_404(Company, id=company_id)
    person = TDSPersonResponsibleDetail.objects.filter(company=company).first()
    states = State.objects.all()

    return render(request, 'company/tcs_person_responsible_details.html', {
        'company': company,
        'person': person,
        'states': states,
        'company_id': company_id,
    })



def vat_tax_rate_details(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    vat_rate = VATTaxRate.objects.filter(company=company).first()
    referer = request.META.get('HTTP_REFERER', '')
    from_next = ''
    if referer:
        parsed = urlparse(referer)
        query = parse_qs(parsed.query)
        if query.get('next', [None])[0] == 'alter':
            from_next = 'alter'


    return render(request, 'company/vat_tax_rate_details.html',{'company': company,
        'company_id': company.id,
        'vat_rate': vat_rate,'next': from_next,
})




def create_vat_tax_rate(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    vat_tax_rate = VATTaxRate.objects.filter(company=company).first()

    if request.method == 'POST':
        next_page = request.POST.get('next')

        tax_rate_raw = request.POST.get('service_tax')
        cess_raw = request.POST.get('education_cess')
        tax_type = request.POST.get('taxability_type')

        tax_rate = tax_rate_raw.strip() if tax_rate_raw and tax_rate_raw.strip() else None
        cess = cess_raw.strip() if cess_raw and cess_raw.strip() else None

        if vat_tax_rate:
            vat_tax_rate.tax_rate = tax_rate
            vat_tax_rate.cess = cess
            vat_tax_rate.tax_type = tax_type
            vat_tax_rate.save()
        else:
            VATTaxRate.objects.create(
                company=company,
                tax_rate=tax_rate,
                cess=cess,
                tax_type=tax_type
            )

        print(f"POST next_page: {next_page}")

        if next_page == 'alter':
            redirect_url = reverse('vat_details', kwargs={'company_id': company.id}) + '?next=alter'
            print(f"Redirecting to (alter): {redirect_url}")
            return redirect(redirect_url)
        else:
            redirect_url = reverse('vat_tax_rate_details', kwargs={'company_id': company.id})
            print(f"Redirecting to (default): {redirect_url}")
            return redirect(redirect_url)

    else:
        referer = request.META.get('HTTP_REFERER', '')
        from_next = ''
        if referer:
            parsed = urlparse(referer)
            query = parse_qs(parsed.query)
            if query.get('next', [None])[0] == 'alter':
                from_next = 'alter'

        print(f"GET referer: {referer}")
        print(f"from_next detected: {from_next}")

        return render(request, 'company/vat_tax_rate_details.html', {
            'company_id': company_id,
            'vat_tax_rate': vat_tax_rate,
            'next': from_next,
        })


def excise_tariff_details(request,company_id):
    company = get_object_or_404(Company, id=company_id)
    excise_tariff = ExciseTariffDetail.objects.filter(company=company).first()
    referer = request.META.get('HTTP_REFERER', '')
    from_next = ''
    if referer:
        parsed = urlparse(referer)
        query = parse_qs(parsed.query)
        if query.get('next', [None])[0] == 'alter':
            from_next = 'alter'

    return render(request,'company/excise_tariff_details.html',{'company':company,'company_id':company_id,'excise_tariff':excise_tariff,'from_next': from_next,})





def create_excise_tariff(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    tariff = ExciseTariffDetail.objects.filter(company=company).first()

    if request.method == 'POST':
        tariff_name = request.POST.get('tariff_name')
        hsn_code = request.POST.get('hsn_code')
        reporting_uom = request.POST.get('reporting_uom')
        valuation_type = request.POST.get('valuation_type')

        def parse_decimal(value):
            try:
                return Decimal(value.strip()) if value and value.strip() else None
            except (InvalidOperation, AttributeError):
                return None

        rate_raw = request.POST.get('rate')
        rate_per_unit_raw = request.POST.get('rate_per_unit')
        print(f"Raw rate: '{rate_raw}', Raw rate_per_unit: '{rate_per_unit_raw}'")

        rate = parse_decimal(request.POST.get('rate'))
        rate_per_unit = parse_decimal(request.POST.get('rate_per_unit'))
        print(f"Parsed rate: {rate}, Parsed rate_per_unit: {rate_per_unit}")

        if tariff:
            tariff.tariff_name = tariff_name
            tariff.hsn_code = hsn_code
            tariff.reporting_uom = reporting_uom
            tariff.valuation_type = valuation_type
            tariff.rate = rate
            tariff.rate_per_unit = rate_per_unit
            tariff.save()
        else:
            ExciseTariffDetail.objects.create(
                company=company,
                tariff_name=tariff_name,
                hsn_code=hsn_code,
                reporting_uom=reporting_uom,
                valuation_type=valuation_type,
                rate=rate,
                rate_per_unit=rate_per_unit
            )

        return redirect('excise_tariff_details', company_id=company.id)

    return render(request, 'company/excise_tariff_form.html', {
        'company': company,
        'tariff': tariff
    })



def create_new_user(request):
    if request.method == 'POST':
        user_name = request.POST.get('users')
        
        if user_name:
            NewUsers.objects.create(users=user_name)
        return redirect(f'{reverse("security_user_access")}?panel=open')
    
    return render(request, 'company/security_user_access.html')




def security_settings_view(request):
    companies = Company.objects.all()
    security_access = None

    company_id = request.GET.get('company_id')
    if company_id:
        security_access = SecuritySettings.objects.filter(company_id=company_id).first()

    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        company = get_object_or_404(Company, id=company_id)

        security_access, created = SecuritySettings.objects.get_or_create(company=company)

        control_user_access = request.POST.get('control_user_access') == 'Yes'
        email_for_browser_access = request.POST.get('email_for_browser_access')
        username = request.POST.get('username')
        password = request.POST.get('password')
        enable_tally_audit = request.POST.get('enable_tally_audit') == 'Yes'
        disallow_educational_mode = request.POST.get('disallow_educational_mode') == 'Yes'
        add_users_after_saving = request.POST.get('add_users_after_saving') == 'Yes'

        security_access.control_user_access = control_user_access
        security_access.email_for_browser_access = email_for_browser_access
        security_access.username = username

        if password:
            security_access.password = make_password(password)

        security_access.enable_tally_audit = enable_tally_audit
        security_access.disallow_educational_mode = disallow_educational_mode
        security_access.add_users_after_saving = add_users_after_saving

        security_access.save()

        return redirect('userDashboard')

    context = {
        'companies': companies,
        'security_access': security_access
    }
    return render(request, 'company/security_user_access.html', context)


def gst_classification(request,company_id):
    company = get_object_or_404(Company, id=company_id)
    referer = request.META.get('HTTP_REFERER', '')
    from_next = ''
    if referer:
        parsed = urlparse(referer)
        query = parse_qs(parsed.query)
        if query.get('next', [None])[0] == 'alter':
            from_next = 'alter'

    return render(request,'company/gst_classification.html',{'company_id':company_id,'company':company,'from_next': from_next,
})



def create_classification(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        name = request.POST.get('name')
        hsn_source = request.POST.get('hsn_source')
        hsn_code = request.POST.get('hsn_code')
        hsn_description = request.POST.get('hsn_description')
        gst_rate_source = request.POST.get('gst_rate_source')
        taxability_type = request.POST.get('taxability_type')
        gst_rate = request.POST.get('gst_rate')

        classification = Classification.objects.create(
            name=name,
            hsn_source=hsn_source,
            hsn_code=hsn_code,
            hsn_description=hsn_description,
            gst_rate_source=gst_rate_source,
            taxability_type=taxability_type,
            gst_rate=gst_rate
        )

        slabRatesJson = request.POST.get('slab_data')
        if slabRatesJson:
            try:
                slab_data_list = json.loads(slabRatesJson)
                slab_rates_to_create = []
                for slab in slab_data_list:
                    slab_rate = SlabRate(
                        classification=classification,
                        greater_than=slab.get('greater_than'),
                        rate_upto=slab.get('rate_upto'),
                        taxability=slab.get('taxability'),
                        gst_rate=slab.get('gst_rate')
                    )
                    slab_rates_to_create.append(slab_rate)
                SlabRate.objects.bulk_create(slab_rates_to_create)
            except json.JSONDecodeError:
                pass

        return redirect(f'/gst_rate_details/{company_id}/?next=classification')

    return render(request, 'company/gst_classification.html')

def outstanding_ledgers(request):
    return render(request,'statement_of_accounts/outstanding/ledgers.html')

def outstanding_groups(request):
    return render(request,'statement_of_accounts/outstanding/group.html')


def cost_categories_view(request):
    categories = CostCategory.objects.all()  


    return render(request, 'masters/cost_categories.html', {
        'categories': categories,
        'current_date': timezone.localdate(),
        'company': 'F3.Company'
    })

def edit_cost_category(request, pk):
    category = get_object_or_404(CostCategory, pk=pk)
    all_categories = CostCategory.objects.all().order_by('name')   

    if request.method == "POST":
        category.name = request.POST.get("name", category.name)
        
        # Handle the checkbox fields
        category.reserve_items = 'reserve_items' in request.POST
        category.non_reserve_items = 'non_reserve_items' in request.POST
        
        category.save()
        # Redirect back to the same edit page
        return redirect(reverse("edit_cost_category", args=[category.pk]))

    return render(request, "masters/cost_category_edit.html", {
        "category": category,
        "all_categories": all_categories  
    })

def currencies_view(request):
    currencies = Currency.objects.all() 
    
    return render(request, 'masters/currencies.html', {
        'currencies': currencies,
        'current_date': timezone.localdate(), 
        'company': 'F3.Company' 
    })


def edit_currencies(request, pk):
    currency = get_object_or_404(Currency, pk=pk)
    all_currencies = Currency.objects.all().order_by('formal_name')

    if request.method == "POST":
        currency.symbol = request.POST.get("symbol", currency.symbol)
        currency.formal_name = request.POST.get("formal_name", currency.formal_name)
        currency.iso_currency_code = request.POST.get("iso_currency_code", currency.iso_currency_code)
        currency.number_of_decimal_places = request.POST.get("number_of_decimal_places", currency.number_of_decimal_places)
        currency.word_amount_adter_decimal = request.POST.get("word_amount_adter_decimal", currency.word_amount_adter_decimal)
        currency.decimal_places_for_amount = request.POST.get("decimal_places_for_amount", currency.decimal_places_for_amount)

        # Handle Boolean fields properly
        currency.suffix_symbol_to_amount = request.POST.get("suffix_symbol_to_amount") == "True"
        
        currency.save()

        RateOfExchange.objects.filter(currency=currency).delete()

        # Process existing rows
        row = 0
        while f"standard_date_{row}" in request.POST:
            standard_date = request.POST.get(f"standard_date_{row}")
            standard_specified_rate = request.POST.get(f"standard_specified_rate_{row}")
            
            # Only create a record if at least one field has data
            if (standard_date or standard_specified_rate or 
                request.POST.get(f"selling_date_{row}") or 
                request.POST.get(f"selling_last_voucher_rate_{row}") or
                request.POST.get(f"selling_specified_rate_{row}") or
                request.POST.get(f"buying_date_{row}") or
                request.POST.get(f"buying_last_voucher_rate_{row}") or
                request.POST.get(f"buying_specified_rate_{row}")):
                
                RateOfExchange.objects.create(
                    currency=currency,
                    standard_date=standard_date or None,
                    standard_specified_rate=standard_specified_rate or None,
                    selling_date=request.POST.get(f"selling_date_{row}") or None,
                    selling_last_voucher_rate=request.POST.get(f"selling_last_voucher_rate_{row}") or None,
                    selling_specified_rate=request.POST.get(f"selling_specified_rate_{row}") or None,
                    buying_date=request.POST.get(f"buying_date_{row}") or None,
                    buying_last_voucher_rate=request.POST.get(f"buying_last_voucher_rate_{row}") or None,
                    buying_specified_rate=request.POST.get(f"buying_specified_rate_{row}") or None,
                )
            row += 1

        # Process the new row (if any data was entered)
        if (request.POST.get("standard_date_new") or 
            request.POST.get("standard_specified_rate_new") or
            request.POST.get("selling_date_new") or
            request.POST.get("selling_last_voucher_rate_new") or
            request.POST.get("selling_specified_rate_new") or
            request.POST.get("buying_date_new") or
            request.POST.get("buying_last_voucher_rate_new") or
            request.POST.get("buying_specified_rate_new")):
            
            RateOfExchange.objects.create(
                currency=currency,
                standard_date=request.POST.get("standard_date_new") or None,
                standard_specified_rate=request.POST.get("standard_specified_rate_new") or None,
                selling_date=request.POST.get("selling_date_new") or None,
                selling_last_voucher_rate=request.POST.get("selling_last_voucher_rate_new") or None,
                selling_specified_rate=request.POST.get("selling_specified_rate_new") or None,
                buying_date=request.POST.get("buying_date_new") or None,
                buying_last_voucher_rate=request.POST.get("buying_last_voucher_rate_new") or None,
                buying_specified_rate=request.POST.get("buying_specified_rate_new") or None,
            )

        return redirect("edit_currencies", pk=currency.pk)

    # Load all rates for rendering
    rates = RateOfExchange.objects.filter(currency=currency).order_by("id")

    return render(request, "masters/currencies_edit.html", {
        "currency": currency,
        "all_currencies": all_currencies,
        "rates": rates,
    })


def scenarios_view(request):
    scenarios = Scenario.objects.all()
    return render(request, 'masters/scenarios.html', {
        'scenarios': scenarios,
        'current_date': timezone.localdate(), 
        'company': '3.Company'  
    })

def edit_scenarios(request, pk):
    scenario = get_object_or_404(Scenario, pk=pk)
    all_scenarios = Scenario.objects.all().order_by('name')
    voucher_types = ListOfVoucherType.objects.all().order_by('name')

    if request.method == "POST":
        scenario.name = request.POST.get("name", scenario.name)
        scenario.include_actuals = "include_actuals" in request.POST
        scenario.exclude_forex = "exclude_forex" in request.POST

        # Process ManyToMany include/exclude fields
        include_ids = request.POST.get("include_ids", "")
        exclude_ids = request.POST.get("exclude_ids", "")
        
        # Split comma-separated values and filter out empty strings
        include_ids_list = [int(id) for id in include_ids.split(',') if id]
        exclude_ids_list = [int(id) for id in exclude_ids.split(',') if id]
        
        scenario.save()  # save first before setting M2M
        scenario.include.set(include_ids_list)
        scenario.exclude.set(exclude_ids_list)

        return redirect("edit_scenarios", pk=pk)

    # Get IDs of selected vouchers for include and exclude
    include_ids = list(scenario.include.values_list('id', flat=True))
    exclude_ids = list(scenario.exclude.values_list('id', flat=True))
    
    return render(request, "masters/scenario_edit.html", {
        "scenario": scenario,
        "all_scenarios": all_scenarios,
        "all_vouchers": voucher_types,
        "include_ids": include_ids,
        "exclude_ids": exclude_ids,
    })


def godowns_view(request):
    godowns = Godowns.objects.all()
    
    # Create a mapping of godown IDs to names for efficient lookup
    godown_map = {}
    for godown in godowns:
        godown_map[str(godown.id)] = godown.name
    
    # Add parent name to each godown object
    for godown in godowns:
        if godown.under and godown.under in godown_map:
            godown.parent_name = godown_map[godown.under]
        else:
            godown.parent_name = "Primary"
    
    return render(request, 'masters/godowns.html', {
        'godowns': godowns,
        'current_date': timezone.localdate(), 
        'company': 'F3.Company'  
    })


def units_view(request):
    # Order units by type first (simple then compound), then by symbol/funit
    units = Unit.objects.all().order_by('type', 'symbol', 'funit')
    return render(request, 'masters/unit.html', {
        'units': units,
        'current_date': timezone.localdate(), 
        'company': 'F3.Company'  
    })


def edit_units(request, pk):
    unit = get_object_or_404(Unit, pk=pk)
    all_units = Unit.objects.all()
    # Get all distinct UQC values from the database
    available_uqc = Unit.objects.exclude(uqc__isnull=True).exclude(uqc__exact='').values_list('uqc', flat=True).distinct()
    
    if request.method == "POST":
        # Update all fields without validation
        unit.type = request.POST.get("type", unit.type)
        unit.formalname = request.POST.get("formalname", unit.formalname)
        unit.symbol = request.POST.get("symbol", unit.symbol)
        unit.uqc = request.POST.get("uqc", unit.uqc)
        unit.decimalno = request.POST.get("decimalno", unit.decimalno)
        unit.funit = request.POST.get("funit", unit.funit)
        unit.sunit = request.POST.get("sunit", unit.sunit)
        unit.tunit = request.POST.get("tunit", unit.tunit)
        
        # Save without validation as requested
        unit.save(force_update=True)
        
        # Redirect to units view after saving
        return redirect("edit_units",pk=pk)
    
    # For GET request, show the form with current unit data
    return render(request, "masters/edit_unit.html", {
        "unit": unit,
        "all_units": all_units,
        "available_uqc": available_uqc,
    })


def unit_create(request, unit_id):
    # Get the current unit (this might be used for context or redirection)
    current_unit = get_object_or_404(Unit, pk=unit_id)
    all_units = Unit.objects.all()
    # Get all distinct UQC values from the database
    available_uqc = Unit.objects.exclude(uqc__isnull=True).exclude(uqc__exact='').values_list('uqc', flat=True).distinct()
    
    # Get the target field from the request (which field to update after creation)
    target_field = request.GET.get('target_field', '')
    
    if request.method == "POST":
        # Create a new unit with all fields from the form
        new_unit = Unit(
            type=request.POST.get("type", "simple"),
            formalname=request.POST.get("formalname", ""),
            symbol=request.POST.get("symbol", ""),
            uqc=request.POST.get("uqc", ""),
            decimalno=request.POST.get("decimalno", 0),
            funit=request.POST.get("funit", ""),
            sunit=request.POST.get("sunit", ""),
            tunit=request.POST.get("tunit", "")
        )
        
        new_unit.save(force_insert=True)
        
        # Redirect back to edit_compound_units with the new unit symbol and target field
        redirect_url = reverse("edit_compound_units", args=[current_unit.pk])
        if target_field:
            redirect_url += f"?new_unit={new_unit.symbol}&target_field={target_field}"
        
        return redirect(redirect_url)
    
    return render(request, "masters/create_unit.html", {
        "unit": current_unit, 
        "all_units": all_units,
        "available_uqc": available_uqc,
        "target_field": target_field,  # Pass target field to template
    })



def edit_compound_units(request, unit_id):
    unit = get_object_or_404(Unit, pk=unit_id)
    all_units = Unit.objects.all().values('id', 'symbol', 'formalname')
    
    # Check if we're returning from unit creation with a new unit
    new_unit = request.GET.get('new_unit', '')
    target_field = request.GET.get('target_field', '')
    
    if request.method == "POST":
        # Get the unit type from the form
        unit_type = request.POST.get("type")
        unit.type = unit_type
        
        if unit_type == "simple":
            # Update simple unit fields
            unit.symbol = request.POST.get("symbol", "")
            unit.formalname = request.POST.get("formalname", "")
            unit.uqc = request.POST.get("uqc", "")
            unit.decimalno = request.POST.get("decimalno", 0)
            
            # Clear compound unit fields
            unit.funit = ""
            unit.sunit = ""
            unit.tunit = ""
            
        else:  # compound unit
            # Update compound unit fields
            unit.funit = request.POST.get("funit", "")
            unit.sunit = request.POST.get("sunit", "")
            unit.tunit = request.POST.get("tunit", "")
            
            # Clear simple unit fields
            unit.symbol = ""
            unit.formalname = ""
            unit.uqc = ""
            unit.decimalno = 0
        
        try:
            unit.save()
            messages.success(request, "Unit updated successfully.")
            return redirect(reverse("edit_compound_units", args=[unit.pk]))
        except Exception as e:
            messages.error(request, f"Error saving unit: {str(e)}")
    
    return render(request, "masters/edit_compound_units.html", {
        "unit": unit,
        "new_unit": new_unit,
        'all_units': all_units,
        "target_field": target_field,
    })


def godown_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        under = request.POST.get('under')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        # Validate input
        if not name:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'Godown name is required.'})
            messages.error(request, 'Godown name is required.')
            return redirect(request.META.get('HTTP_REFERER', 'godowns_view'))

        try:
            # Create godown
            if under == 'primary' or not under:
                new_godown = Godowns.objects.create(name=name)
            else:
                parent_godown = get_object_or_404(Godowns, id=under)
                new_godown = Godowns.objects.create(name=name, under=parent_godown)

            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'godown_id': new_godown.id,
                    'name': new_godown.name,
                    'message': f'Godown "{name}" created successfully.'
                })
            messages.success(request, f'Godown "{name}" created successfully.')
            return redirect(request.META.get('HTTP_REFERER', 'godowns_view'))

        except Exception as e:
            error_msg = f'Error creating godown: {str(e)}'
            if is_ajax:
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect(request.META.get('HTTP_REFERER', 'godowns_view'))

    # If not POST, redirect back (never JSON here)
    return redirect('godowns_view')

def edit_godowns(request, pk):
    godown = get_object_or_404(Godowns, pk=pk)
    # Exclude the current godown from the list to prevent circular references
    all_godowns = Godowns.objects.exclude(pk=pk).order_by('name')

    if request.method == "POST":
        name = request.POST.get("name")
        under_value = request.POST.get("under")
        
        # Validate the name
        if not name:
            messages.error(request, "Godown name is required.")
            return render(request, "masters/edit_godowns.html", {
                "godown": godown,
                "all_godowns": all_godowns
            })
        
        # Update the godown
        godown.name = name
        
        # Handle the under field - store the primary key as string
        if under_value == "primary":
            godown.under = None  # Set to None for primary godowns
        elif under_value:
            # Store the primary key as string
            godown.under = under_value
        else:
            godown.under = None
        
        godown.save()
        messages.success(request, f"Godown '{godown.name}' updated successfully.")
        return redirect(reverse("edit_godowns", args=[godown.pk]))

    return render(request, "masters/edit_godowns.html", {
        "godown": godown,
        "all_godowns": all_godowns
    })
