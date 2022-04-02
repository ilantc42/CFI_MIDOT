# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import sys
from datetime import datetime
from enum import Enum
from typing import Optional, Union

import attr
from attrs_strict import type_validator
from marshmallow import Schema, SchemaOpts, fields, post_dump
from marshmallow_enum import EnumField


class TurnoverCategory(Enum):
    CAT_500K = (0, 500_000)
    CAT_1M = (500_000, 1_000_000)
    CAT_3M = (1_000_000, 3_000_000)
    CAT_5M = (3_000_000, 5_000_000)
    CAT_10M = (5_000_000, 10_000_000)
    CAT_50M = (10_000_000, 50_000_000)
    CAT_MAX = (50_000_000, sys.maxsize)

    def __init__(self, min_value: int, max_value: int):
        self.min_value = min_value
        self.max_value = max_value

    def __lt__(self, other: "TurnoverCategory"):
        return self.min_value < other.min_value

    @classmethod
    def from_value(cls, value: int) -> "TurnoverCategory":
        for turnover_category in cls:
            if (
                value >= turnover_category.min_value
                and value < turnover_category.max_value
            ):
                return turnover_category
        raise ValueError(f"Could not find turnover category for value: {value}")


def _add_type_validator(cls, fields):
    validated_fields = []
    for field in fields:
        if field.validator is not None:
            validated_fields.append(field)
            continue
        validated_fields.append(field.evolve(validator=type_validator()))
    return validated_fields


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoTopRecipientSalary:
    recipient_title: str
    gross_salary_in_nis: float


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoTopRecipientsSalaries:
    ngo_id: int = attr.ib(converter=int)
    report_year: int = attr.ib(converter=int)
    top_earners_salaries: list[NgoTopRecipientSalary]


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoGeneralInfo:
    ngo_name: str
    ngo_year_founded: Optional[int] = None
    ngo_goal: Optional[str] = None
    volunteers_num: Optional[int] = None
    employees_num: Optional[int] = None
    ngo_members_num: Optional[int] = None

    main_activity_field: Optional[str] = None
    activity_fields: Optional[list[str]] = None
    target_audience: Optional[list[str]] = None


@attr.s(
    frozen=True, auto_attribs=True, kw_only=True, field_transformer=_add_type_validator
)
class NgoFinanceInfo:
    report_year: int = attr.ib(converter=int)
    ngo_id: int = attr.ib(converter=int)

    allocations_from_government: Union[int, float] = 0
    allocations_from_local_authority: Union[int, float] = 0
    allocations_from_other_sources: Union[int, float] = 0

    donations_from_aboard: Union[int, float] = 0
    donations_from_israel: Union[int, float] = 0

    service_income_from_country: Union[int, float] = 0
    service_income_from_local_authority: Union[int, float] = 0
    service_income_from_other: Union[int, float] = 0

    other_income_from_other_sources: Union[int, float] = 0
    other_income_members_fee: Union[int, float] = 0

    expenses_other: Union[int, float] = 0
    expenses_for_management: Union[int, float] = 0
    expenses_salary_for_management: Union[int, float] = 0
    expenses_salary_for_activities: Union[int, float] = 0
    other_expenses_for_activities: Union[int, float] = 0
    donations_of_monetary_value: Union[int, float] = 0

    # ------------ Computed ------------
    total_allocations_income: Union[int, float] = attr.ib(init=False)
    total_donations_income: Union[int, float] = attr.ib(init=False)
    total_service_income: Union[int, float] = attr.ib(init=False)
    total_other_income: Union[int, float] = attr.ib(init=False)
    total_expenses: Union[int, float] = attr.ib(init=False)
    # ------------ Ratios ------------
    program_expense_ratio: Optional[float] = attr.ib(init=False)
    administrative_expense_ratio: Optional[float] = attr.ib(init=False)
    total_allocations_income_ratio: Union[int, float] = attr.ib(init=False)
    total_donations_income_ratio: Union[int, float] = attr.ib(init=False)
    total_service_income_ratio: Union[int, float] = attr.ib(init=False)
    total_other_income_ratio: Union[int, float] = attr.ib(init=False)
    # Used for ranking
    # yearly_turnover: Union[int, float] = attr.ib(init=False)
    yearly_profit_precent: Union[int, float] = attr.ib(init=False)
    max_income_ratio: Union[int, float] = attr.ib(init=False)

    @total_allocations_income.default
    def _total_allocations_income(self) -> Union[int, float]:
        return (
            self.allocations_from_government
            + self.allocations_from_local_authority
            + self.allocations_from_other_sources
        )

    @total_donations_income.default
    def _total_donations_income(self) -> Union[int, float]:
        return (
            self.donations_from_aboard
            + self.donations_from_israel
            + self.donations_of_monetary_value
        )

    @total_service_income.default
    def _total_service_income(self) -> Union[int, float]:
        return (
            self.service_income_from_country
            + self.service_income_from_local_authority
            + self.service_income_from_other
        )

    @total_other_income.default
    def _total_other_income(self) -> Union[int, float]:
        return self.other_income_from_other_sources + self.other_income_members_fee

    @total_expenses.default
    def _total_expenses(self) -> Union[int, float]:
        return (
            self.expenses_other
            + self.other_expenses_for_activities
            + self.expenses_for_management
            + self.expenses_salary_for_management
            + self.expenses_salary_for_activities
        )

    @property
    def yearly_turnover(self) -> Union[int, float]:
        return (
            self.total_allocations_income
            + self.total_donations_income
            + self.total_service_income
            + self.total_other_income
        )

    # ------------ Categories ------------
    @property
    def yearly_turnover_category(self) -> TurnoverCategory:
        return TurnoverCategory.from_value(self.yearly_turnover)

    # 1. spread ratio stability
    # 2. Custom color per category rank
    # 3. Cell for max stability rank cat
    # 4. deicit -> profitability
    # 5. OCR / Current data

    # ------------ Ratios ------------
    @total_allocations_income_ratio.default
    def _total_allocations_income_ratio(self) -> Union[int, float]:
        # Precentage of total allocations income to yearly turnover
        if not self.yearly_turnover:
            return 0
        return self.total_allocations_income / self.yearly_turnover

    @total_donations_income_ratio.default
    def _total_donations_income_ratio(self) -> Union[int, float]:
        # Precentage of total donations income to yearly turnover
        if not self.yearly_turnover:
            return 0
        return self.total_donations_income / self.yearly_turnover

    @total_service_income_ratio.default
    def _total_service_income_ratio(self) -> Union[int, float]:
        # Precentage of total service income to yearly turnover
        if not self.yearly_turnover:
            return 0
        return self.total_service_income / self.yearly_turnover

    @total_other_income_ratio.default
    def _total_other_income_ratio(self) -> Union[int, float]:
        # Precentage of total other income to yearly turnover
        if not self.yearly_turnover:
            return 0
        return self.total_other_income / self.yearly_turnover

    @max_income_ratio.default
    def _max_income_ratio(self) -> float:
        return max(
            self.total_allocations_income_ratio,
            self.total_donations_income_ratio,
            self.total_service_income_ratio,
            self.total_other_income_ratio,
        )

    @yearly_profit_precent.default
    def _yearly_profit_precent(self) -> Union[int, float]:
        # Precantage of yearly profit to yearly turnover
        if not self.yearly_turnover:
            return 0
        return (self.yearly_turnover - self.total_expenses) / self.yearly_turnover

    @program_expense_ratio.default
    def _program_expense_ratio(self) -> Optional[float]:

        total_program_expenses = (
            self.other_expenses_for_activities + self.expenses_salary_for_activities
        )

        if total_program_expenses == 0 or self.total_expenses == 0:
            return None

        return total_program_expenses / self.total_expenses

    @administrative_expense_ratio.default
    def _administrative_expense_ratio(self) -> Optional[float]:

        total_administrative_expenses = (
            self.expenses_salary_for_management
            + self.expenses_for_management
            + self.expenses_other
        )

        if total_administrative_expenses == 0 or self.total_expenses == 0:
            return None

        return total_administrative_expenses / self.total_expenses


@attr.s(frozen=True, auto_attribs=True, field_transformer=_add_type_validator)
class NgoInfo:
    ngo_id: int

    general_info: NgoGeneralInfo
    financial_info: Optional[list[NgoFinanceInfo]] = attr.ib(
        factory=list,
        converter=lambda reports: sorted(
            reports, key=lambda report: report.report_year
        ),
    )
    top_earners_info: Optional[list[NgoTopRecipientsSalaries]] = attr.ib(
        factory=list,
        converter=lambda reports: sorted(
            reports, key=lambda report: report.report_year
        ),
    )

    @property
    def last_financial_info(self) -> Optional[NgoFinanceInfo]:
        if not self.financial_info:
            return None
        return self.financial_info[-1]

    @property
    def last_top_earners_info(self) -> Optional[NgoTopRecipientsSalaries]:
        if not self.top_earners_info:
            return None

        return self.top_earners_info[-1]

    @classmethod
    def from_resource_items(cls, ngo_id: int, resources_items: dict) -> "NgoInfo":
        return cls(ngo_id=ngo_id, **resources_items)


class OrderedSchema(Schema):
    class OrderedOpts(SchemaOpts):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.ordered = True

    OPTIONS_CLASS = OrderedOpts


class NgoTopRecipientSalarySchema(OrderedSchema):
    recipient_title = fields.String()
    gross_salary_in_nis = fields.Float()


class NgoTopRecipientsSalariesSchema(OrderedSchema):
    ngo_id = fields.Int()
    report_year = fields.Int()
    top_earners_salaries = fields.Nested(NgoTopRecipientSalarySchema, many=True)


class NgoFinanceInfoSchema(OrderedSchema):
    ngo_id = fields.Int()
    report_year = fields.Int()

    yearly_turnover = fields.Number()
    yearly_turnover_category = EnumField(TurnoverCategory)
    # ------------ Ratios ------------
    yearly_profit_precent = fields.Number()
    # ------------ Ratios ------------
    program_expense_ratio = fields.Number(allow_none=True)
    administrative_expense_ratio = fields.Number(allow_none=True)
    total_allocations_income_ratio = fields.Number()
    total_donations_income_ratio = fields.Number()
    total_service_income_ratio = fields.Number()
    total_other_income_ratio = fields.Number()
    # ------------ Totals ------------
    total_allocations_income = fields.Number()
    total_donations_income = fields.Number()
    total_service_income = fields.Number()
    total_other_income = fields.Number()
    total_expenses = fields.Number()

    # ------------ Details ------------
    allocations_from_government = fields.Number()
    allocations_from_local_authority = fields.Number()
    allocations_from_other_sources = fields.Number()
    donations_from_aboard = fields.Number()
    donations_from_israel = fields.Number()
    service_income_from_country = fields.Number()
    service_income_from_local_authority = fields.Number()
    service_income_from_other = fields.Number()
    other_income_from_other_sources = fields.Number()
    other_income_members_fee = fields.Number()
    expenses_other = fields.Number()
    expenses_for_management = fields.Number()
    expenses_salary_for_management = fields.Number()
    expenses_salary_for_activities = fields.Number()
    other_expenses_for_activities = fields.Number()
    donations_of_monetary_value = fields.Number()


CURRENT_YEAR = datetime.now().year


class NGOInfoSchema(OrderedSchema):
    """Flatten schema for NgoInfo"""

    ngo_id = fields.Int()
    ngo_name = fields.Str(attribute="general_info.ngo_name", allow_none=True)
    ngo_goal = fields.Str(attribute="general_info.ngo_goal", allow_none=True)
    ngo_year_founded = fields.Int(
        attribute="general_info.ngo_year_founded", allow_none=True
    )
    last_financial_report_year = fields.Int(attribute="last_financial_info.report_year")

    volunteers_num = fields.Int(
        attribute="general_info.volunteers_num", allow_none=True
    )
    employees_num = fields.Int(attribute="general_info.employees_num", allow_none=True)
    ngo_members_num = fields.Int(
        attribute="general_info.ngo_members_num", allow_none=True
    )
    main_activity_field = fields.Str(
        attribute="general_info.main_activity_field", allow_none=True
    )
    activity_fields = fields.List(
        fields.Str(), attribute="general_info.activity_fields", allow_none=True
    )
    target_audience = fields.List(
        fields.Str(), attribute="general_info.target_audience", allow_none=True
    )

    max_income_ratio = fields.Number(
        attribute="last_financial_info.max_income_ratio", allow_none=True
    )

    # Income sources ratios
    total_allocations_income_ratio = fields.Number(
        attribute="last_financial_info.total_allocations_income_ratio", allow_none=True
    )
    total_donations_income_ratio = fields.Number(
        attribute="last_financial_info.total_donations_income_ratio", allow_none=True
    )
    total_service_income_ratio = fields.Number(
        attribute="last_financial_info.total_service_income_ratio", allow_none=True
    )
    total_other_income_ratio = fields.Number(
        attribute="last_financial_info.total_other_income_ratio", allow_none=True
    )

    # Additional ratios
    program_expense_ratio = fields.Number(
        attribute="last_financial_info.program_expense_ratio", allow_none=True
    )
    administrative_expense_ratio = fields.Number(
        attribute="last_financial_info.administrative_expense_ratio", allow_none=True
    )
    # -------------------------------------------------------------------------
    # Computed totals
    total_allocations_income = fields.Number(
        attribute="last_financial_info.total_allocations_income"
    )
    total_donations_income = fields.Number(
        attribute="last_financial_info.total_donations_income"
    )
    total_service_income = fields.Number(
        attribute="last_financial_info.total_service_income"
    )
    total_other_income = fields.Number(
        attribute="last_financial_info.total_other_income"
    )

    total_expenses = fields.Number(attribute="last_financial_info.total_expenses")

    financial_info_history = fields.List(
        fields.Nested(NgoFinanceInfoSchema), attribute="financial_info"
    )
    # top_earners_info_history = fields.List(
    #     fields.Nested(NgoTopRecipientsSalariesSchema), attribute="top_earners_info"
    # )

    # Detailed financial info
    expenses_other = fields.Number(attribute="last_financial_info.expenses_other")
    expenses_for_management = fields.Number(
        attribute="last_financial_info.expenses_for_management"
    )
    expenses_salary_for_management = fields.Number(
        attribute="last_financial_info.expenses_salary_for_management"
    )
    expenses_salary_for_activities = fields.Number(
        attribute="last_financial_info.expenses_salary_for_activities"
    )
    other_expenses_for_activities = fields.Number(
        attribute="last_financial_info.other_expenses_for_activities"
    )

    allocations_from_government = fields.Number(
        attribute="last_financial_info.allocations_from_government"
    )
    allocations_from_local_authority = fields.Number(
        attribute="last_financial_info.allocations_from_local_authority"
    )
    allocations_from_other_sources = fields.Number(
        attribute="last_financial_info.allocations_from_other_sources"
    )

    donations_from_aboard = fields.Number(
        attribute="last_financial_info.donations_from_aboard"
    )
    donations_from_israel = fields.Number(
        attribute="last_financial_info.donations_from_israel"
    )
    donations_of_monetary_value = fields.Number(
        attribute="last_financial_info.donations_of_monetary_value"
    )

    service_income_from_country = fields.Number(
        attribute="last_financial_info.service_income_from_country"
    )
    service_income_from_local_authority = fields.Number(
        attribute="last_financial_info.service_income_from_local_authority"
    )
    service_income_from_other = fields.Number(
        attribute="last_financial_info.service_income_from_other"
    )
    other_income_from_other_sources = fields.Number(
        attribute="last_financial_info.other_income_from_other_sources"
    )
    other_income_members_fee = fields.Number(
        attribute="last_financial_info.other_income_members_fee"
    )

    @post_dump
    def dump_schema(self, data: dict, **kwargs) -> dict:
        """
        Add dynamic financial fields to the schema
        """
        # We copy the data dict to avoid modifying the original OrderedDict
        data_copy = data.copy()
        for field_name, values in data.items():
            if field_name == "financial_info_history":
                for report in values:
                    dynamic_keys = [
                        "yearly_turnover",
                        "yearly_turnover_category",
                        "yearly_profit_precent",
                    ]
                    for dynamic_key in dynamic_keys:
                        data_copy[f"{report['report_year']}__{dynamic_key}"] = report[
                            dynamic_key
                        ]

        # Delete this to reduce the size of the response
        del data_copy["financial_info_history"]
        return data_copy
