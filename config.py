import os
from dataclasses import dataclass
from dotenv import load_dotenv
    
load_dotenv()

@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv("DATABASE_URL")
    maptiler_key: str = os.getenv("MAPTILER_KEY")
    map_style: str = os.getenv("MAPTILER_STYLE", "satellite-v2")
    dash_host: str = os.getenv("DASH_HOST", "127.0.0.1")
    dash_port: int = int(os.getenv("DASH_PORT", "8050"))
    debug: bool = os.getenv("DEBUG", "1") == "1"
    gps_scale: float = float(os.getenv("PPI_GPS_SCALE", "10000000"))
    background_width: int = int(os.getenv("MAP_BG_WIDTH", "900"))
    background_height: int = int(os.getenv("MAP_BG_HEIGHT", "520"))
    logging_config: str = ""
    logging_level: str ="DEBUG"
    stop: None = None
    rssi_bins: str = """    
        {'min':-999.0, 'max':-100.0, 'desc':"≤ -100 dBm",      'color':'#ee82ee');
        ('min':-100.0, 'max':-90.0,  'desc':'-100 to -90 dBm', 'color':'#4b0082');   
        ('min':-90.0,  'max':-80.0,  'desc':'-90 to -80 dBm',  'color':'#0000ff');
        ('min':-80.0,  'max':-70.0,  'desc':'-80 to -70 dBm',  'color':'#00ff00');
        ('min':-70.0,  'max':-60.0,  'desc':'-70 to -60 dBm',  'color':'#ffff00');
        ('min':-60.0,  'max':-50.0,  'desc':'-60 to -50 dBm',  'color':'#ffa500');
        ('min':-50.0,  'max':999.0,  'desc':'> -50 dBm',       'color':'#ff0000')
    """
    base_schema_sql: str = """
    CREATE TABLE IF NOT EXISTS frames (
        frame_id         BIGSERIAL PRIMARY KEY,
        ts               TIMESTAMPTZ,
        dot11_type       INTEGER,
        dot11_subtype    INTEGER,
        ta               MACADDR,
        ra               MACADDR,
        bssid            MACADDR,
        rssi_dbm         DOUBLE PRECISION,
        rssi_bin         TEXT NOT NULL DEFAULT '≤ -100 dBm',
        lat              DOUBLE PRECISION,
        lon              DOUBLE PRECISION,
        x                DOUBLE PRECISION,
        y                DOUBLE PRECISION
    );
    
    CREATE TABLE IF NOT EXISTS mac_nodes (
        mac                  MACADDR NOT NULL,
        frames_seen          INTEGER NOT NULL,
        transmitted_frames   INTEGER NOT NULL,
        received_frames      INTEGER NOT NULL,
        distinct_neighbors   INTEGER NOT NULL,
        avg_rssi_dbm         DOUBLE PRECISION,
        min_lat              DOUBLE PRECISION,
        max_lat              DOUBLE PRECISION,
        min_lon              DOUBLE PRECISION,
        max_lon              DOUBLE PRECISION,
        centroid_vec         VECTOR(2),
        PRIMARY KEY (mac)
    );
    
    CREATE TABLE IF NOT EXISTS mac_edges (
        mac_a            MACADDR NOT NULL,
        mac_b            MACADDR NOT NULL,
        frame_count      INTEGER NOT NULL,
        avg_rssi_dbm     DOUBLE PRECISION,
        PRIMARY KEY (mac_a, mac_b)
    );
    """

settings = Settings(
    logging_config='''{
        "version": 1,
        "disable_existing_loggers": "False",
        "formatters": {
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"]
        }
    }'''
)




