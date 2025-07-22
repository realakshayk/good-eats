import subprocess
try:
    import playwright
except ImportError:
    subprocess.check_call(['pip', 'install', 'playwright'])
print('Installing Playwright browsers...')
subprocess.check_call(['playwright', 'install', 'chromium'])
print('Chromium installed.') 