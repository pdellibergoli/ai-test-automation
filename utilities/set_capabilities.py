def set_appium_caps(platform, device_name, udid, app_package, app_activity):
    if platform.lower() == 'ios':
        custom_caps = {     
            #'automationName': 'XCUITest',
            'bundle_id': app_package               
        }
    elif platform.lower() == 'android':
        custom_caps = {   
            #'automationName': 'uiautomator2',
            'app_package': app_package,
            'app_activity': app_activity                  
        }
    custom_caps['platform_name'] = platform
    custom_caps['device_name'] = device_name
    custom_caps['udid'] = udid
    custom_caps['noReset'] = True

    return custom_caps

def set_mobile_cloud_caps(platformName, deviceName, app_id, test_id, descrizione):
    custom_caps = {
        'platform_name': platformName,
        'device_name': deviceName,
        'app': app_id,
        'noReset': True,
        'isRealMobile': True,
        'build': f'{test_id} - {descrizione}',
        'name': descrizione,
        'project': 'iCorner TA',
    }

    return custom_caps

def set_web_cloud_caps(platformName, deviceName, app_id, test_id, descrizione):
    custom_caps = {
        'platform_name': platformName,
        'device_name': deviceName,
        'app': app_id,
        'noReset': True,
        'isRealMobile': True,
        'build': test_id,
        'name': descrizione,
        'project': 'iCorner TA',
    }

    return custom_caps