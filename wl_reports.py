from apps.data.models import ReportSummary
from apps.data.trafficguard.models import CampaignSummary
from django.db.models import Sum
import pandas as pd
from apps.main_app.wl_rulebook import WhiteLabelRuleBookMultiPublishers
from django.contrib.auth.models import User

class WlReportManager():


    def __init__(self, wl_configuration, start_date, end_date):
        self.wl_configuration = wl_configuration
        self.wlpublisher_df = pd.DataFrame([
            {
                'publisher_id': wl_publisher.publisher.id,
                'bucket': wl_publisher.get_bucket_display()
            }
            for wl_publisher in self.wl_configuration.wlpublisher_set.all()
        ], columns=['publisher_id', 'bucket'])
        self.start_date = start_date
        self.end_date = end_date
        self.wl_rulebook = WhiteLabelRuleBookMultiPublishers()

    def get_tg_reports(self):
        # after WL revshare (synced to campaigns)
        reports = (
            CampaignSummary.objects.filter(
                date__range=(self.start_date, self.end_date),
                crossroads_user_id__in=self.wlpublisher_df.publisher_id.unique().tolist()
            )
            .values('crossroads_user_id')
            .annotate(Sum('total_visitors'), Sum('tracked_visitors'), pub_client_rev=Sum('publisher_revenue_amount') )
            .values('date','pub_client_rev', 'total_visitors__sum', 'tracked_visitors__sum',  'crossroads_user_id')
        )

        df = pd.DataFrame(list(reports))
        df = df.merge(self.wlpublisher_df, how='left', left_on='crossroads_user_id', right_on='publisher_id')
        return df

    def get_owner_rev(self, row):
        return self.wl_rulebook.apply_rule_reverse(row['crossroads_user_id'], row['date'],row['pub_client_rev'] )


    def cal_diff (self, row):
        try:
            return float(row['owner_rev']) - float(row['pub_client_rev'])
        except:
            return 0.0
    def get_reports(self):

        df = self.get_tg_reports()
        df['owner_rev'] = df.apply(self.get_owner_rev, axis=1)
        users = pd.DataFrame(list(User.objects.filter(id__in=df['crossroads_user_id'].unique().tolist() ).values('username', 'id') ))
        df = df.merge(users, left_on='crossroads_user_id', right_on='id', how='left')
        df = df.groupby(['crossroads_user_id', 'username', 'bucket']).sum().reset_index()
        df['diff'] = df.apply(self.cal_diff, axis=1)

        df['diff'] = df['diff'].round(decimals=2)
        df['owner_rev'] = df['owner_rev'].round(decimals=2)
        return df


    def empty_df(self):
        return pd.DataFrame()
