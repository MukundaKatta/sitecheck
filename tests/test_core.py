"""Tests for Sitecheck."""
from src.core import Sitecheck
def test_init(): assert Sitecheck().get_stats()["ops"] == 0
def test_op(): c = Sitecheck(); c.detect(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Sitecheck(); [c.detect() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Sitecheck(); c.detect(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Sitecheck(); r = c.detect(); assert r["service"] == "sitecheck"
