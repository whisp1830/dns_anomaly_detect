import sys,os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(BASE_DIR)

from handlers import *
import connectors


c = connectors.Connector()

router = [
        (r"/base", BaseHandler, dict(connectors=c)),
        (r"/long", LongDomainHandler, dict(connectors=c)),
        (r"/trend/([-\w.]+)", TrendHandler, dict(connectors=c)),
        (r"/daily/([-\w]+)" , DailyPageHandler, dict(connectors=c)),
        (r"/hourly/([-\w]+)", HourlyPageHandler, dict(connectors=c)),
        (r"/domain/([-\w.]+)", DomainHandler, dict(connectors=c)),
        (r"/host/([-\w.]+)", HostHandler, dict(connectors=c)),
        (r"/testd3", D3ApiHandler, dict(connectors=c)),
        (r"/realtime", D3PageHandler, dict(connectors=c)),
        (r"/pollution", PollutePageHandler, dict(connectors=c)),
        (r"/alerts", AlertPageHandler, dict(connectors=c)),
        (r"/client/([-\w.]+)", ClientHandler, dict(connectors=c)),
        (r"/firstseen", FirstSeenHandler, dict(connectors=c))
]