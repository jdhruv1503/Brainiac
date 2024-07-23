import logging
import requests
import json
import time
from concurrent.futures import ThreadPoolExecutor
from threading import current_thread
from schemas import DBSession, AlphaResult


class WQSession(requests.Session):
    def __init__(self, json_fn="credentials.json"):
        super().__init__()
        for handler in logging.root.handlers:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s: %(message)s"
        )
        self.json_fn = json_fn
        self.login()
        old_get, old_post = self.get, self.post

        def new_get(*args, **kwargs):
            try:
                return old_get(*args, **kwargs)
            except:
                return new_get(*args, **kwargs)

        def new_post(*args, **kwargs):
            try:
                return old_post(*args, **kwargs)
            except:
                return new_post(*args, **kwargs)

        self.get, self.post = new_get, new_post
        self.login_expired = False
        self.rows_processed = []

    def login(self):
        with open(self.json_fn, "r") as f:
            creds = json.loads(f.read())
            email, password = creds["email"], creds["password"]
            self.auth = (email, password)
            r = self.post("https://api.worldquantbrain.com/authentication")
        if "user" not in r.json():
            if "inquiry" in r.json():
                input(
                    f"Please complete biometric authentication at {r.url}/persona?inquiry={r.json()['inquiry']} before continuing..."
                )
                self.post(f"{r.url}/persona", json=r.json())
            else:
                print(f"WARNING! {r.json()}")
                input("Press enter to quit...")
        logging.info("Logged in to WQBrain!")

    def simulate(self, data):
        self.rows_processed = []

        def process_simulation(simulation):
            if self.login_expired:
                return  # expired crendentials

            thread = current_thread().name
            alpha = simulation["code"].strip()
            delay = simulation.get("delay", 1)
            universe = simulation.get("universe", "TOP3000")
            truncation = simulation.get("truncation", 0.1)
            region = simulation.get("region", "USA")
            decay = simulation.get("decay", 6)
            neutralization = simulation.get("neutralization", "SUBINDUSTRY").upper()
            pasteurization = simulation.get("pasteurization", "ON")
            nan = simulation.get("nanHandling", "OFF")
            logging.info(f"{thread} -- Simulating alpha: {alpha}")
            while True:
                # keep sending a post request until the simulation link is found
                try:
                    r = self.post(
                        "https://api.worldquantbrain.com/simulations",
                        json={
                            "regular": alpha,
                            "type": "REGULAR",
                            "settings": {
                                "nanHandling": nan,
                                "instrumentType": "EQUITY",
                                "delay": delay,
                                "universe": universe,
                                "truncation": truncation,
                                "unitHandling": "VERIFY",
                                "pasteurization": pasteurization,
                                "region": region,
                                "language": "FASTEXPR",
                                "decay": decay,
                                "neutralization": neutralization,
                                "visualization": False,
                            },
                        },
                    )
                    nxt = r.headers["Location"]
                    break
                except:
                    try:
                        if "credentials" in r.json()["detail"]:
                            self.login_expired = True
                            return
                    except:
                        logging.info(
                            f"{thread} -- {r.content}"
                        )  # usually gateway timeout
                        return
            logging.info(f"{thread} -- Obtained simulation link: {nxt}")
            ok = True
            while True:
                r = self.get(nxt).json()
                if "alpha" in r:
                    alpha_link = r["alpha"]
                    break
                try:
                    logging.info(
                        f"{thread} -- Waiting for simulation to end ({int(100*r['progress'])}%)"
                    )
                except Exception as e:
                    ok = (False, r["message"])
                    break
                time.sleep(10)
            if ok != True:
                logging.info(
                    f"{thread} -- Issue when sending simulation request: {ok[1]}"
                )
                row = [
                    0,
                    delay,
                    region,
                    neutralization,
                    decay,
                    truncation,
                    0,
                    0,
                    0,
                    "FAIL",
                    0,
                    -1,
                    universe,
                    nxt,
                    alpha,
                ]
                sql_write_failed_alpha(row)

            else:
                r = self.get(
                    f"https://api.worldquantbrain.com/alphas/{alpha_link}"
                ).json()
                logging.info(
                    f"{thread} -- Obtained alpha link: https://platform.worldquantbrain.com/alpha/{alpha_link}"
                )

                alpha_result = AlphaResult(
                    alpha_id=r["id"],
                    alpha_type=r["type"],
                    author=r["author"],
                    instrument_type=r["settings"]["instrumentType"],
                    region=r["settings"]["region"],
                    universe=r["settings"]["universe"],
                    delay=r["settings"]["delay"],
                    decay=r["settings"]["decay"],
                    neutralization=r["settings"]["neutralization"],
                    truncation=r["settings"]["truncation"],
                    pasteurization=r["settings"]["pasteurization"],
                    unit_handling=r["settings"]["unitHandling"],
                    nan_handling=r["settings"]["nanHandling"],
                    language=r["settings"]["language"],
                    visualization=r["settings"]["visualization"],
                    regular_code=r["regular"]["code"],
                    date_created=r["dateCreated"],
                    date_submitted=r["dateSubmitted"],
                    date_modified=r["dateModified"],
                    name=r["name"],
                    grade=r["grade"],
                    stage=r["stage"],
                    status=r["status"],
                    is_pnl=r["is"]["pnl"],
                    is_book_size=r["is"]["bookSize"],
                    is_long_count=r["is"]["longCount"],
                    is_short_count=r["is"]["shortCount"],
                    is_turnover=r["is"]["turnover"],
                    is_returns=r["is"]["returns"],
                    is_drawdown=r["is"]["drawdown"],
                    is_margin=r["is"]["margin"],
                    is_fitness=r["is"]["fitness"],
                    is_sharpe=r["is"]["sharpe"],
                    is_start_date=r["is"]["startDate"],
                    is_check_low_sharpe_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_sharpe_limit=next(
                        (
                            check["limit"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_sharpe_value=next(
                        (
                            check["value"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_fitness_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_FITNESS"
                        ),
                        None,
                    ),
                    is_check_low_fitness_limit=next(
                        (
                            check["limit"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_FITNESS"
                        ),
                        None,
                    ),
                    is_check_low_fitness_value=next(
                        (
                            check["value"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_FITNESS"
                        ),
                        None,
                    ),
                    is_check_low_turnover_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_TURNOVER"
                        ),
                        None,
                    ),
                    is_check_low_turnover_limit=next(
                        (
                            check["limit"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_TURNOVER"
                        ),
                        None,
                    ),
                    is_check_low_turnover_value=next(
                        (
                            check["value"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_TURNOVER"
                        ),
                        None,
                    ),
                    is_check_high_turnover_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "HIGH_TURNOVER"
                        ),
                        None,
                    ),
                    is_check_high_turnover_limit=next(
                        (
                            check["limit"]
                            for check in r["is"]["checks"]
                            if check["name"] == "HIGH_TURNOVER"
                        ),
                        None,
                    ),
                    is_check_high_turnover_value=next(
                        (
                            check["value"]
                            for check in r["is"]["checks"]
                            if check["name"] == "HIGH_TURNOVER"
                        ),
                        None,
                    ),
                    is_check_concentrated_weight_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "CONCENTRATED_WEIGHT"
                        ),
                        None,
                    ),
                    is_check_low_sub_universe_sharpe_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_SUB_UNIVERSE_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_sub_universe_sharpe_limit=next(
                        (
                            check["limit"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_SUB_UNIVERSE_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_sub_universe_sharpe_value=next(
                        (
                            check["value"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_SUB_UNIVERSE_SHARPE"
                        ),
                        None,
                    ),
                    is_check_units_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "UNITS"
                        ),
                        None,
                    ),
                    is_check_units_message=next(
                        (
                            check["message"]
                            for check in r["is"]["checks"]
                            if check["name"] == "UNITS"
                        ),
                        None,
                    ),
                    is_check_self_correlation_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "SELF_CORRELATION"
                        ),
                        None,
                    ),
                    is_check_matches_competition_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "MATCHES_COMPETITION"
                        ),
                        None,
                    ),
                    is_check_low_returns_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_RETURNS"
                        ),
                        None,
                    ),
                    is_check_low_returns_limit=next(
                        (
                            check["limit"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_RETURNS"
                        ),
                        None,
                    ),
                    is_check_low_returns_value=next(
                        (
                            check["value"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_RETURNS"
                        ),
                        None,
                    ),
                    is_check_low_robust_universe_sharpe_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_ROBUST_UNIVERSE_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_robust_universe_sharpe_ratio=next(
                        (
                            check["ratio"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_ROBUST_UNIVERSE_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_robust_universe_sharpe_limit=next(
                        (
                            check["limit"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_ROBUST_UNIVERSE_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_robust_universe_sharpe_value=next(
                        (
                            check["value"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_ROBUST_UNIVERSE_SHARPE"
                        ),
                        None,
                    ),
                    is_check_low_robust_universe_returns_result=next(
                        (
                            check["result"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_ROBUST_UNIVERSE_RETURNS"
                        ),
                        None,
                    ),
                    is_check_low_robust_universe_returns_ratio=next(
                        (
                            check["ratio"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_ROBUST_UNIVERSE_RETURNS"
                        ),
                        None,
                    ),
                    is_check_low_robust_universe_returns_limit=next(
                        (
                            check["limit"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_ROBUST_UNIVERSE_RETURNS"
                        ),
                        None,
                    ),
                    is_check_low_robust_universe_returns_value=next(
                        (
                            check["value"]
                            for check in r["is"]["checks"]
                            if check["name"] == "LOW_ROBUST_UNIVERSE_RETURNS"
                        ),
                        None,
                    ),
                    alpha_link=f"https://platform.worldquantbrain.com/alpha/{alpha_link}",
                    alpha_code=alpha,
                )

            print(r)

            # Add the AlphaResult object to the session and commit the changes
            DBSession.add(alpha_result)
            DBSession.commit()

            self.rows_processed.append(simulation)
            logging.info(f"{thread} -- Result added to the database!")

        try:
            for handler in logging.root.handlers:
                logging.root.removeHandler(handler)

            log_file = f"logging/log.log"
            logging.basicConfig(
                encoding="utf-8",
                level=logging.INFO,
                format="%(asctime)s: %(message)s",
                filename=log_file,
            )

            with ThreadPoolExecutor(
                max_workers=10
            ) as executor:  # 10 threads, only 3 can go in concurrently so this is no harm
                _ = executor.map(lambda sim: process_simulation(sim), data)

        except Exception as e:
            print(f"Issue occurred! {type(e).__name__}: {e}")

        return [sim for sim in data if sim not in self.rows_processed]
