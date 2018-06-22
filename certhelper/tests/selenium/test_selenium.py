from django.urls import reverse


def test_anonymous(live_server, firefox):
    firefox.get('%s%s' % (live_server.url, reverse('certhelper:list')))
    assert firefox.title == "TkDQMDoctor: List"
