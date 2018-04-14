# Proxy-Grabber
Simple http proxy grabber and checker

# Installation

```
$ pip3 install proxy-grabber
```

# Usage
``` python
import ProxyGrabber
grabber = ProxyGrabber('./data/useragents.list') # File with user-agents

# --- Adding proxies ---

# Parse proxy from different sources
# You can call generate_proxy_list() without arguments if you want to grab as more proxies as possible
grabber.grab_proxies(proxy_limit=100)

# [optional]
# Also you can add some proxies from file
grabber.load_proxies('./data/proxy.list')

# [optional]
# Or you can add proxy manually
grabber.add_proxies(['ip:port', 'ip:port', ...])

# --- Checking proxies ---
grabber.check_proxies()

# --- Get results ---
grabber.get_proxy() # Random checked proxy
grabber.get_checked_proxies() # All checked proxies
grabber.save_proxies('./data/checked_proxies.list') # Save checked proxies to file
```

