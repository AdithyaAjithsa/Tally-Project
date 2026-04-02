from django.db import models
from django.contrib.auth.models import User



# Create your models here.

class State(models.Model):
    name = models.CharField(max_length=128,null=True)

class Country(models.Model):
    name = models.CharField(max_length=128,null=True)


class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    data_path = models.CharField(max_length=255,null=True)
    name = models.CharField(max_length=255,null=True)
    mailing_name = models.CharField(max_length=255,null=True)
    address = models.TextField(null=True)
    state = models.ForeignKey(State,on_delete=models.CASCADE,null=True)
    country = models.ForeignKey(Country,on_delete=models.CASCADE,null=True)
    pincode = models.CharField(max_length=100,null=True)
    telephone = models.CharField(max_length=200,null=True)
    mobile = models.CharField(max_length=200,null=True)
    fax = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    base_currency_symbol = models.CharField(max_length=100,null=True)
    formal_name = models.CharField(max_length=255,null=True)
    
    financial_year_start = models.DateField(null=True)
    books_start_date = models.DateField(null=True)
    
    def __str__(self):
        return self.name


class DateRange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    date_range = models.CharField(max_length=100,null=True)

    def __str__(self):
        return f"{self.user.username}: {self.date_range}"
    

class CurrentDate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    current_date = models.DateField(null=True)

    def __str__(self):
        return f"{self.user.username}: {self.current_date}"


class GSTDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)  
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    registration_type = models.CharField(max_length=50,null=True)
    assessee_of_other_territory = models.BooleanField(default=False)
    gstin_uin = models.CharField(max_length=20, blank=True, null=True)
    periodicity_gstr1 = models.CharField(max_length=100, null=True)
    kerala_flood_cess = models.BooleanField(default=False)
    gst_username = models.CharField(max_length=50, blank=True, null=True)
    mode_of_filing = models.CharField(max_length=200, null=True)
    einvoice_applicable = models.BooleanField(default=False)
    einvoice_applicable_from = models.DateField(blank=True, null=True)
    invoice_bill_from_place = models.CharField(max_length=100, blank=True, null=True)
    ewaybill_applicable = models.BooleanField(default=False)
    ewaybill_applicable_from = models.DateField(blank=True, null=True)
    ewaybill_interstate = models.BooleanField(default=False)
    create_another_registration = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company.name} GST Registration"


class GSTRateDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    hsn_sac_details = models.CharField(max_length=100, blank=True, null=True)
    hsn_sac = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    classification_hsn = models.CharField(max_length=100, blank=True, null=True) 
    gst_rate_details_choice = models.CharField(max_length=100, blank=True, null=True) 
    taxability_type = models.CharField(max_length=100, blank=True, null=True)
    classification_gst = models.CharField(max_length=100, blank=True, null=True) 
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    interstate_threshold = models.CharField(max_length=255,null=True)  
    intrastate_threshold = models.CharField(max_length=255,null=True) 
    threshold_includes = models.CharField(max_length=100, blank=True, null=True)  
    create_summary_for = models.CharField(max_length=100, blank=True, null=True)
    minimum_length = models.IntegerField(blank=True, null=True)
    show_gst_advances = models.BooleanField(default=False)
    application_from = models.CharField(max_length=100, blank=True, null=True)
    update_gst_status_vouchers = models.BooleanField(default=False)
    update_gst_status_returns = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company.name} GST Rate Details"



class TDSDeductorDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    tan_registration_number = models.CharField(max_length=100, null=True, blank=True)
    tan = models.CharField(max_length=100, null=True, blank=True)
    deductor_type = models.CharField(max_length=100, null=True, blank=True)
    deductor_branch = models.CharField(max_length=100, null=True, blank=True)
    alter_person_responsible = models.BooleanField(default=False)
    ignore_it_exemption_limit = models.BooleanField(default=False)
    activate_tds_stock_item = models.BooleanField(default=False)

    def __str__(self):
        return f"TDS Details for {self.company.name}"
    

class TCSCollectorDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    tan_registration_number = models.CharField(max_length=20, null=True, blank=True)
    tax_eduction_collection_account_number = models.CharField(max_length=20, null=True, blank=True)
    collector_type = models.CharField(max_length=100, null=True, blank=True)
    collector_branch = models.CharField(max_length=100, null=True, blank=True)
    alter_person_responsible = models.BooleanField(default=False)
    ignore_it_exemption_limit = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company.name} TDS Collector Details"



class VATDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    tin = models.CharField(max_length=50, null=True, blank=True)
    interstate_sales_tax_number = models.CharField(max_length=50, null=True, blank=True)
    alter_tax_rate_details = models.BooleanField(default=False)
    define_vat_commodity = models.BooleanField(default=False)
    deactivate_from = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.company.name} VAT Details"



class ExciseDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, null=True, blank=True)
    unit_name = models.CharField(max_length=100,null=True)
    address = models.TextField()
    pincode = models.CharField(max_length=100,null=True)
    telephone_number = models.CharField(max_length=100, null=True, blank=True)
    registration_type = models.CharField(max_length=100,null=True)
    type_of_manufacturer = models.CharField(max_length=100, null=True, blank=True)
    ecc_number = models.CharField(max_length=100,null=True)
    set_alter_tariff = models.BooleanField(default=False)
    define_tariff_masters = models.BooleanField(default=False)
    deactivate_from = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.company.name} Excise Details"


class ServiceTaxDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    registration_number = models.CharField(max_length=100,null=True)
    organisation_type = models.CharField(max_length=100,null=True)
    set_alter_service_tax = models.BooleanField(default=False)
    define_service_category_masters = models.BooleanField(default=False)
    reverse_charge_applicable = models.BooleanField(default=False)
    deactivate_from = models.DateField(null=True, blank=True)
    is_monthly_format = models.CharField(max_length=10, null=True, blank=True)
    compute_tax_liability = models.CharField(max_length=20, null=True, blank=True)


    def __str__(self):
        return f"{self.company.name} Service Tax Details"
    

class ServiceTaxRate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100,null=True)
    service_tax = models.DecimalField(max_digits=5, decimal_places=2, default=0,null=True)
    education_cess = models.DecimalField(max_digits=5, decimal_places=2, default=0,null=True)
    secondary_education_cess = models.DecimalField(max_digits=5, decimal_places=2, default=0,null=True)
    swachh_bharat_cess = models.DecimalField(max_digits=5, decimal_places=2, default=0,null=True)
    krishi_kalyan_cess = models.DecimalField(max_digits=5, decimal_places=2, default=0,null=True)
    is_monthly_format = models.BooleanField(default=False, null=True, blank=True)
    compute_tax_liability = models.CharField( max_length=100, null=True, blank=True)
    def __str__(self):
        return f"{self.company.name} - {self.name}"



class PayrollStatutoryDetails(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True, blank=True)
    pf_company_code = models.CharField(max_length=100)
    pf_account_group_code = models.CharField(max_length=100, blank=True, null=True)
    pf_security_code = models.CharField(max_length=100, blank=True, null=True)
    esi_company_code = models.CharField(max_length=100, blank=True, null=True)
    esi_branch_office = models.CharField(max_length=100, blank=True, null=True)
    esi_working_days = models.PositiveIntegerField(blank=True, null=True)
    nps_registration_number = models.CharField(max_length=100, blank=True, null=True)
    nps_branch_office_number = models.CharField(max_length=100, blank=True, null=True)
    tan = models.CharField(max_length=100, blank=True, null=True)
    tan_registration_number = models.CharField(max_length=100, blank=True, null=True)
    income_class_circle = models.CharField(max_length=100, blank=True, null=True)
    deductor_type = models.CharField(max_length=100, blank=True, null=True)
    deductor_branch = models.CharField(max_length=100, blank=True, null=True)
    person_responsible = models.CharField(max_length=100, blank=True, null=True)
    son_daughter_of = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    pan = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payroll Statutory Details for {self.company.name}"
    

class CompanyAddress(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    mailing_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=100, blank=True, null=True)
    fax = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.mailing_name or 'Address'} for {self.company.name}"
    

class MerchantProfile(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100, blank=True, null=True)
    merchant_name = models.CharField(max_length=100, blank=True, null=True)
    create_another = models.BooleanField(default=False)
    merchant_id = models.CharField(max_length=100, blank=True, null=True)
    registered_email = models.CharField(max_length=100,blank=True, null=True)
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.payment_method}"
    


class CompanyFeatures(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    maintain_accounts = models.BooleanField(default=False)
    enable_bill_wise_entry = models.BooleanField(default=False)
    enable_cost_centres = models.BooleanField(default=False)
    enable_interest_calculations = models.BooleanField(default=False)
    maintain_inventory = models.BooleanField(default=False)
    integrate_accounts_inventory = models.BooleanField(default=False)
    enable_multiple_price_levels = models.BooleanField(default=False)
    enable_batches = models.BooleanField(default=False)
    maintain_expiry_for_batches = models.BooleanField(default=False)
    enable_job_order_processing = models.BooleanField(default=False)
    enable_cost_tracking = models.BooleanField(default=False)
    enable_job_costing = models.BooleanField(default=False)
    use_discount_column = models.BooleanField(default=False)
    use_actual_billed_qty_columns = models.BooleanField(default=False)
    enable_gst = models.BooleanField(default=False)
    alter_gst_details = models.BooleanField(default=False)
    enable_tds = models.BooleanField(default=False)
    enable_tcs = models.BooleanField(default=False)
    enable_vat = models.BooleanField(default=False)
    enable_excise = models.BooleanField(default=False)
    enable_service_tax = models.BooleanField(default=False)
    enable_browser_access = models.BooleanField(default=False)
    enable_remote_access = models.BooleanField(default=False)
    maintain_payroll = models.BooleanField(default=False)
    enable_payroll_statutory = models.BooleanField(default=False)
    enable_payment_request = models.BooleanField(default=False)
    enable_multiple_address = models.BooleanField(default=False)
    mark_modified_vouchers = models.BooleanField(default=False)

    def __str__(self):
        return f"Features for {self.company.name}"



class TallyVaultSetting(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE,null=True)
    vault_password = models.CharField(max_length=255,null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tally Vault for {self.company.name}"
    


#NEW

class GSTEffectiveDate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    date = models.DateField(null=True)


class GSTSettings(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    return_type = models.CharField(max_length=100,null=True)

    def __str__(self):
        return f"{self.company} - {self.return_type}"


class TDSPersonResponsibleDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    parent_name = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    pan = models.CharField(max_length=100, null=True, blank=True)
    flat_no = models.CharField(max_length=100, null=True, blank=True)
    building_name = models.CharField(max_length=100, null=True, blank=True)
    road = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    std_code = models.CharField(max_length=50, null=True, blank=True)
    telephone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.company.name} - Person Responsible"
    

class SlabRate(models.Model):
    classification = models.ForeignKey('Classification',on_delete=models.CASCADE,related_name='slab_rates', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    greater_than = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rate_upto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxability = models.CharField(max_length=50, null=True, blank=True)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def _str_(self):
        return f"{self.classification.name} | ₹{self.greater_than} - ₹{self.rate_upto} @ {self.gst_rate}%"


class Classification(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    hsn_source = models.CharField(max_length=128, null=True, blank=True)
    hsn_code = models.CharField(max_length=128, null=True, blank=True)
    hsn_description = models.CharField(max_length=128, null=True, blank=True)
    gst_rate_source = models.CharField(max_length=128, null=True, blank=True)
    gst_classification = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    taxability_type = models.CharField(max_length=128, null=True, blank=True)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # slab_rate = models.ManyToManyField(SlabRate, blank=True)

    def _str_(self):
        return self.name
    

class TCSPersonResponsibleDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,null=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    parent_name = models.CharField(max_length=100, null=True, blank=True)
    designation = models.CharField(max_length=100, null=True, blank=True)
    pan = models.CharField(max_length=100, null=True, blank=True)
    flat_no = models.CharField(max_length=100, null=True, blank=True)
    building_name = models.CharField(max_length=100, null=True, blank=True)
    road = models.CharField(max_length=100, null=True, blank=True)
    area = models.CharField(max_length=100, null=True, blank=True)
    town = models.CharField(max_length=100, null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    pincode = models.CharField(max_length=50, null=True, blank=True)
    mobile = models.CharField(max_length=50, null=True, blank=True)
    std_code = models.CharField(max_length=50, null=True, blank=True)
    telephone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.company.name} - Person Responsible"



class VATTaxRate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='service_tax_rates',null=True)
    tax_rate = models.DecimalField(max_digits=50, decimal_places=2, default=0.00,null=True)
    cess = models.DecimalField(max_digits=50, decimal_places=2, default=0.00,null=True)
    tax_type = models.CharField(max_length=100,null=True)

    def __str__(self):
        return f"{self.company.name} - {self.tax_type}"
    


class ExciseTariffDetail(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='excise_tariff_details',null=True)
    tariff_name = models.CharField(max_length=200,null=True)
    hsn_code = models.CharField(max_length=50,null=True)
    reporting_uom = models.CharField(max_length=50,null=True)
    valuation_type = models.CharField(max_length=100,null=True)
    rate = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)
    rate_per_unit = models.DecimalField(max_digits=50, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.tariff_name} ({self.company.name})"


class NewUsers(models.Model):
    users = models.CharField(max_length=255,null=True)


class SecuritySettings(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)
    control_user_access = models.BooleanField(default=False)
    email_for_browser_access = models.CharField(max_length=255,null=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)

    enable_tally_audit = models.BooleanField(default=False)
    disallow_educational_mode = models.BooleanField(default=False)
    add_users_after_saving = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SecuritySettings for {self.company.name}"
    
class ListOfVoucherType(models.Model):
    name = models.CharField(max_length=100, unique=True,null=True)
    abbreviation = models.CharField(max_length=100, blank=True, null=True)

    def _str_(self):
        return self.name
    
class Scenario(models.Model):
    name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Scenario name for reference"
    )
    include_actuals = models.BooleanField(
        default=False,
        help_text="Whether to include actual transactions"
    )
    include = models.ManyToManyField(
        ListOfVoucherType,
        related_name='included_in_scenarios',
        blank=True,
        help_text="Voucher types included in scenario"
    )
    exclude = models.ManyToManyField(
        ListOfVoucherType,
        related_name='excluded_from_scenarios',
        blank=True,
        help_text="Voucher types excluded from scenario"
    )

    def __str__(self):
        return self.name or f"Scenario {self.id}"

class CostCategory(models.Model):
    name = models.CharField(max_length=100)
    reserve_items = models.BooleanField(default=False)
    non_reserve_items = models.BooleanField(default=False)

    def _str_(self):
        return self.name


class Currency(models.Model):
    symbol = models.CharField(max_length=10)
    formal_name = models.CharField(max_length=100)
    iso_currency_code = models.CharField(max_length=10)
    number_of_decimal_places = models.PositiveSmallIntegerField(default=2)
    show_amount_in_millions = models.BooleanField(default=False)
    suffix_symbol_to_amount = models.BooleanField(default=False)
    add_space_between_amount = models.BooleanField(default=False)
    word_amount_adter_decimal = models.CharField(max_length=50, blank=True, null=True)
    decimal_places_for_amount = models.PositiveSmallIntegerField(default=0)

    def _str_(self):
        return f"{self.formal_name} ({self.symbol})"


class ListofGroups(models.Model):
    id = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=128)


class RateOfExchange(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="rates",null=True) 
    standard_date = models.DateField(null=True, blank=True)
    standard_specified_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    selling_date = models.DateField(null=True, blank=True)
    selling_last_voucher_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    selling_specified_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    buying_date = models.DateField(null=True, blank=True)
    buying_last_voucher_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    buying_specified_rate = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)

    def __str__(self):
        return f"Rates for {self.currency.formal_name} on {self.standard_date}"
    

class Godowns(models.Model):
    name = models.CharField(max_length=128)
    under = models.CharField(max_length=100,null=True, blank=True)
    grouping_of_godowns = models.CharField(max_length=128, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    allow_storage = models.BooleanField(default=True)
    third_party_storage_details = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'godown'
        verbose_name = 'Godown'
        verbose_name_plural = 'Godowns'

    def _str_(self):
        return self.name
    

class Unit(models.Model):
    UNIT_TYPE_CHOICES = [
        ('simple', 'Simple'),
        ('compound', 'Compound'),
    ]

    type = models.CharField(max_length=10, choices=UNIT_TYPE_CHOICES, default='simple')
    
    symbol = models.CharField(max_length=50, null=True, blank=True)
    formalname = models.CharField(max_length=100, null=True, blank=True)
    uqc = models.CharField(max_length=100, default='Not Applicable', null=True, blank=True)
    decimalno = models.PositiveIntegerField(default=0)

    funit = models.CharField("First Unit", max_length=100, null=True, blank=True)
    sunit = models.CharField("Conversion Factor", max_length=100, null=True, blank=True)
    tunit = models.CharField("Second Unit", max_length=100, null=True, blank=True)

    def __str__(self):
        if self.type == 'simple' and self.symbol:
            return f"{self.symbol} ({self.formalname})"
        elif self.type == 'compound' and self.funit and self.sunit and self.tunit:
            return f"{self.funit} = {self.sunit} {self.tunit}"
        return f"Unnamed {self.get_type_display()} Unit"
