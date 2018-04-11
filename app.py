import logging
import time
from collections import defaultdict, namedtuple
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import fire
import requests
import yaspin
from retry import retry

log = logging.getLogger()

with_retry_policy = retry(
    (
        requests.ConnectionError,
        requests.HTTPError,
        requests.ConnectTimeout,
        requests.ReadTimeout,
        requests.RequestException,
    ),
    delay=1,
    tries=5,
    backoff=2,
)


class AppStatus(namedtuple("Status", "version, total_cnt, success_cnt")):
    pass


class AgregatedStatus(namedtuple("Status", "version, total_cnt, success_cnt")):

    @property
    def rate(self) -> float:
        return self.success_cnt / self.total_cnt if total_cnt > 0 else 1.0

    def add(self, status):
        self.version = status.version
        self.total_cnt += status.total_cnt
        self.success_cnt += status.success_cnt


@with_retry_policy
def check_endpoint(
    host_prefix: str, host_group="twitter.com"
) -> (AppStatus or None, Exception or None):

    r = requests.get(f"http://{host_prefix}.{host_group}/status")
    if not r.ok:
        return None, RuntimeError(
            f"Could not get {host_prefix}.{host_group}  details={r.content[:200]}"
        )

    # Schema
    # [{"Application":"Cache2","Version":"1.0.1","Uptime":4637719417,
    # "Request_Count":5194800029,"Error_Count":1042813251,"Success_Count":4151986778},
    try:
        p = r.json()
        return AppStatus(
            version=p.get("Version", "Unknown"),
            total_cnt=p.get("Request_Count", 0),
            success_cnt=p.get("Success_Count", 0),
        ), None

    except ValueError:
        return None, RuntimeError(
            f"Could not get {host_prefix}.{host_group} bad payload {r.content[:200]}"
        )


def _run(servers_file, workers, stage):
    stage.write("> Reading file")

    with open(servers_file, "r") as fp:
        data = fp.read()
    servers = [datum.strip("\t ") for datum in data.split("\n") if datum]
    pool = ThreadPoolExecutor(max_workers=workers)
    stage.write("> Brewing coffee")
    results = []
    for server in servers:
        log.debug("Spawning for %s", server)
        fut = pool.submit(check_endpoint, (server,))
        results.append(fut)
    stage.write("> Creating  a thread pool")

    group_by_version: {str: AgregatedStatus} = defaultdict(
        lambda s: AgregatedStatus("", 0, 0)
    )
    stage.write("> Processing")
    for r in results:
        try:
            status, err = r.result(timeout=60)
        except TimeoutError:
            continue

        except Exception:
            log.exception("Skipping")
            continue

        if err:
            log.error("%s", err)
            continue

        group_by_version[status.version].add(status)

    print("Version | Success rate")
    for version, agg in group_by_version.items():
        print(f"{version} | {agg.rate()}")
    stage.ok("✔")


def run(servers_file: str, workers: int = 5):
    """Diagnostic cli app

    Arguments:
        servers_file {str} -- a plain text file with list of servers

    Keyword Arguments:
        workers {int} -- number of threads (default: {5})
    """

    with yaspin.yaspin(text="Checking status", color="cyan") as stage:
        _run(servers_file=servers_file, workers=workers, stage=stage)
    return


def entrypoint():
    fire.Fire(run)


if __name__ == "__main__":
    entrypoint()
