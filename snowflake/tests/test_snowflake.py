# (C) Datadog, Inc. 2020-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
from decimal import Decimal
from typing import Any, Dict

import mock

from datadog_checks.base.stubs.aggregator import AggregatorStub
from datadog_checks.snowflake import SnowflakeCheck, queries

EXPECTED_TAGS = ['account:test_acct.us-central1.gcp']


# def test_check(dd_run_check, instance):
#     check = SnowflakeCheck('snowflake', {}, [instance])
#     dd_run_check(check)


def test_storage_metrics(dd_run_check, aggregator, instance):
    # type: (AggregatorStub, Dict[str, Any]) -> None

    expected_storage = [(Decimal('0.000000'), Decimal('1206.000000'), Decimal('19.200000'))]
    with mock.patch('datadog_checks.snowflake.SnowflakeCheck.execute_query_raw', return_value=expected_storage):
        check = SnowflakeCheck('snowflake', {}, [instance])
        check._conn = mock.MagicMock()
        check._query_manager.queries = [queries.StorageUsageMetrics]
        dd_run_check(check)

    aggregator.assert_metric('snowflake.storage.storage_bytes.total', value=0.0, tags=EXPECTED_TAGS)
    aggregator.assert_metric('snowflake.storage.stage_bytes.total', value=1206.0, tags=EXPECTED_TAGS)
    aggregator.assert_metric('snowflake.storage.failsafe_bytes.total', value=19.2, tags=EXPECTED_TAGS)


def test_db_storage_metrics(dd_run_check, aggregator, instance):
    # type: (AggregatorStub, Dict[str, Any]) -> None

    expected_db_storage_usage = [('SNOWFLAKE_DB', Decimal('133.000000'), Decimal('9.100000'))]
    expected_tags = EXPECTED_TAGS + ['database:SNOWFLAKE_DB']
    with mock.patch(
        'datadog_checks.snowflake.SnowflakeCheck.execute_query_raw', return_value=expected_db_storage_usage
    ):
        check = SnowflakeCheck('snowflake', {}, [instance])
        check._conn = mock.MagicMock()
        check._query_manager.queries = [queries.DatabaseStorageMetrics]
        dd_run_check(check)
    aggregator.assert_metric('snowflake.storage.database.storage_bytes', value=133.0, tags=expected_tags)
    aggregator.assert_metric('snowflake.storage.database.failsafe_bytes', value=9.1, tags=expected_tags)


def test_credit_usage_metrics(dd_run_check, aggregator, instance):
    # type: (AggregatorStub, Dict[str, Any]) -> None

    expected_credit_usage = [
        ('WAREHOUSE_METERING', 'COMPUTE_WH', Decimal('0.218333333'), Decimal('0.000566111'), Decimal('0.218899444')),
        ('WAREHOUSE_METERING', 'COMPUTE_WH', Decimal('0.166666667'), Decimal('0.000270556'), Decimal('0.166937223')),
        ('WAREHOUSE_METERING', 'COMPUTE_WH', Decimal('0E-9'), Decimal('0.000014722'), Decimal('0.000014722')),
        ('WAREHOUSE_METERING', 'COMPUTE_WH', Decimal('0.183611111'), Decimal('0.000303333'), Decimal('0.183914444')),
        ('WAREHOUSE_METERING', 'COMPUTE_WH', Decimal('0.016666667'), Decimal('0E-9'), Decimal('0.016666667')),
    ]
    expected_tags = EXPECTED_TAGS + ['service_type:WAREHOUSE_METERING', 'service:COMPUTE_WH']
    with mock.patch('datadog_checks.snowflake.SnowflakeCheck.execute_query_raw', return_value=expected_credit_usage):
        check = SnowflakeCheck('snowflake', {}, [instance])
        check._conn = mock.MagicMock()
        check._query_manager.queries = [queries.CreditUsage]
        dd_run_check(check)

    aggregator.assert_metric('snowflake.billing.cloud_service', count=5, tags=expected_tags)
    aggregator.assert_metric('snowflake.billing.total', count=5)
    aggregator.assert_metric('snowflake.billing.virtual_warehouse', count=5)


def test_warehouse_usage_metrics(dd_run_check, aggregator, instance):
    # type: (AggregatorStub, Dict[str, Any]) -> None

    expected_wh_usage = [
        ('COMPUTE_WH', Decimal('0.286111111'), Decimal('0.002308056'), Decimal('0.288419167')),
        ('COMPUTE_WH', Decimal('0.459166667'), Decimal('0.001471667'), Decimal('0.460638333')),
    ]
    expected_tags = EXPECTED_TAGS + ['warehouse:COMPUTE_WH']
    with mock.patch('datadog_checks.snowflake.SnowflakeCheck.execute_query_raw', return_value=expected_wh_usage):
        check = SnowflakeCheck('snowflake', {}, [instance])
        check._conn = mock.MagicMock()
        check._query_manager.queries = [queries.WarehouseCreditUsage]
        dd_run_check(check)

    aggregator.assert_metric('snowflake.billing.warehouse.cloud_service', count=2, tags=expected_tags)
    aggregator.assert_metric('snowflake.billing.warehouse.total', count=2, tags=expected_tags)
    aggregator.assert_metric('snowflake.billing.warehouse.virtual_warehouse', count=2, tags=expected_tags)
