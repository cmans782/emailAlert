from mailalert.config import Config
import jinja2
import flask
import pytz

blueprint = flask.Blueprint('filters', __name__)

# registers this function as a Jinja filter
@blueprint.app_template_filter()
def datetimefilter(value, format="%-I:%M %p"):

    # set tz to the timezone in config.py
    tz = pytz.timezone(Config.TIMEZONE)
    utc = pytz.timezone('UTC')
    value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
    # convert UTC time to local time
    local_dt = value.astimezone(tz)
    return local_dt.strftime(format)


@blueprint.app_template_filter()
def admin_datetime_filter(view, value):

    # set tz to the timezone in config.py
    tz = pytz.timezone(Config.TIMEZONE)
    utc = pytz.timezone('UTC')
    value = utc.localize(value, is_dst=None).astimezone(pytz.utc)
    # convert UTC time to local time
    local_dt = value.astimezone(tz)
    return local_dt.strftime("%Y-%m-%d %H:%M:%S")
