# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup

#### FUNCTIONS 1.2
import requests  # import requests to make a post request

def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url):
    try:
        r = requests.get(url, verify=False)
        count = 1
        while r.status_code == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = requests.get(url, verify=False)
        sourceFilename = r.headers.get('Content-Disposition')
        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.status_code == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False


def validate(filename, file_url):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string


#### VARIABLES 1.0

entity_id = "E1535_CBC_gov"
url = "https://www.chelmsford.gov.uk/your-council/finance-and-transparency/transparency/expenditure-over-250/"
errors = 0
data = []
year_d = {"AjaxManager":"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$updConsolePanel|espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$resultsPerPageControl$ddlRecords",
"PostBack":"",
"ScrollPos":"0",
"LinkState":"",
"__EVENTTARGET":"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$resultsPerPageControl$ddlRecords",
"__EVENTARGUMENT":"",
"__LASTFOCUS":"",
"__VIEWSTATEZIP":"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",
"__VIEWSTATE":"/wEPZmThWZPWMdA9jzp4uc5Lg0U2I0LL3cagA6sQ2aSnpjOErw==",
"PageNotifications$hfState":"",
"floatingwindowTab_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset":"0",
"floatingwindowVisible_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset":"false",
"floatingwindowConfig_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset":'{"name":"UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset","title":"New","width":800,"height":650,"collapsible":false,"closable":true,"modal":true,"autoScroll":false,"autoTabs":false,"shadow":true,"constrain":false,"minWidth":650,"maxWidth":1024,"minHeight":500,"maxHeight":1000,"buttons":[{"id":"ok","text":"Next"},{"id":"cancel","text":"Cancel"}],"showOnLoad":false,"focusOnLoad":false,"postbackOnClose":true,"postbackOnResize":false,"postbackOnCancel":true,"maintainPostbackVisibility":true,"controlId":"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset","contentElementId":"floatingwindowContent_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset","selectedTabHiddenFieldId":"floatingwindowTab_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset","visibilityStateHiddenFieldId":"floatingwindowVisible_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset"}',
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$cKeywords$txtKeywords":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$consoleMessagePanel$hfState":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$resultsPerPageControl$ddlRecords":"61",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$notificationPanel$hfState":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_ee106874-da19-4ca0-8692-7d6ae7374ced$cContainer$txtText":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_1080c401-24c8-44cb-97f7-5014d46a3a42$cContainer$txtText":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_24bc0b1e-cf59-4998-9aa7-8c4202b84087$cContainer$txtText":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_d1ba2900-a1ef-40e7-a2fb-88183d9afbc8$cContainer$txtText":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_dded97bb-9ebd-44ad-bde5-194d553e68cf$cContainer$TextArea":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_6e4ad32c-2ea2-467f-898a-aab615387810$cContainer$DatePickerField$txtDate":"20/06/2018",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_6e4ad32c-2ea2-467f-898a-aab615387810$cContainer$DatePickerField$hfInitialDate":"20/06/2018",
"g-recaptcha-response":"",
"__VIEWSTATEGENERATOR":"2362A2C6",
"__EVENTVALIDATION":"/wEdADUT0XeWrvGw8DZUCDYiHUdAxJMl82VmbJPmhJ8RpBZ23vw12ex4WxOx+EKxvDyp2IrEGisIDESiFFMN8gWfSyLQEPnj3/6iNzxs+I1ATengOejQvdzSnFI2RGbtk7fv2LTzUY68prbuXNaHDYez9qIN1cI7MV+unCUFbdSklmB38ayX438Re7MB+bS+c7dposM5nyvdUMTFHWhhiKLon/wrSj9X1amNHUlZ3p47XyAIXFh2E4f6LvTk10rZSI/PaHBkO5zw7SOPoL2HzvfUh5NNodVBz8MQ1fyAaGEN+aeNIw7tBSn1c7dzq2iHUrQIYgvnryclOnjrzlrKiHngCm7QhDkhbAak4aonopvvFKRcQ3cQhpD2EBAZyNQO/HcM4gfSXfemvXUSz1vm7CNQ/WOsEiEIBkkSDrgkwaaDuOJWkMNnyTQ6C6MdK+D4AxdbF6aN4wOJab/at+mh+ADCrj5IKH+O0o6GMmFR5r3kydcIFjyrA1o9zjuBBvKSRrFW7gxd+8jIloTRE9IvQBO4Qlex9CzRZYdLp8kplIywhM21vejxxB/kSYdIduq1jRqaaqPpb3ZmeJJ3RTeqrmgAE6LMqqw5yA9dmxGpjDDaxjnRj0UzZhdbU/z4ml1sDtgR/x236w0deW4gRHcU+rnabSoil4cjL/g6Zk8za6XPzIFKe1XXVXvEmjEO4N3VEUZt/SLZ8LaB+WIxdX3cBgS9afcrW7D68Bh1ygziP97i6m94/z//N4EdiIGs0VQZJM84zge8yJVeLLtIVJk7+/ix/1wBJxuScNaYIXpMDeWu2wfOZq4zNDct2trm8wM/qcNwDVJYXRGKamGx7gEM2nkqJEnzJ/Ua+d8Qvn81v+t00X+godIYhr2qpafnIgEuFIVaQ1HIrQOWDMZV9qv5C494Kh6eVZ2YwbutYIvp8wuHMs/la2Sp2kfbDK38ZmzdvbyzOelmADOiNdatB8W+agBiGYJ0uHPQ72IK/LD+SieKzysQF7gbGRw2aI93uK4vcAUIbc1/xoEzRhxEZ1Bl6KpyTbPqVohDLgjPj5/sMAib6/++0fxbBWdl1z3Q9BFXN5+vhqAz1j6V0pqFx84EKT8wddMMSXG1r+KxF2+98SBtkTLkFwsAx36wtSioO6Y2eWnYcNqykzVGxUc/dq41P0ZIBhvd",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset$ctnBinaryUpload$tabBinaryUpload$notificationPanel$hfState":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset$ctnBinaryUpload$tabBinaryUpload$pnlBinaryUpload$sbumBinary$state":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset$ctnBinaryUpload$tabContentUpload$notificationPanel$hfState":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset$ctnBinaryUpload$ctnBinaryUpload_SelectedTabHiddenField":"0",
"__ASYNCPOST":"true"}
year_cookies = {'Cookie': 'ASP.NET_SessionId=abglqq4bugendhqvecyso5uu; __AntiXsrfToken=2fe24b05b31449a5b3e3befff46e3967; _ga=GA1.3.43744148.1529479996; _gid=GA1.3.1070353058.1529479996; AllowEasysiteCookies=true; nmstat=1529480007479; socitm_exclude_me27=true; _gat=1; _gat_UA-89913601-1=1'}
file_d = {"PostBack":"",
"ScrollPos":"0",
"LinkState":"",
"__EVENTTARGET":"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$consoleTable$cell_1_49220",
"__EVENTARGUMENT":"",
"__LASTFOCUS":"",
"__VIEWSTATEZIP":"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",
"__VIEWSTATE":"/wEPZmThWZPWMdA9jzp4uc5Lg0U2I0LL3cagA6sQ2aSnpjOErw==",
"PageNotifications$hfState":"",
"floatingwindowTab_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset":"0",
"floatingwindowVisible_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset":"false",
"floatingwindowConfig_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset":'{"name":"UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset","title":"New","width":800,"height":650,"collapsible":false,"closable":true,"modal":true,"autoScroll":false,"autoTabs":false,"shadow":true,"constrain":false,"minWidth":650,"maxWidth":1024,"minHeight":500,"maxHeight":1000,"buttons":[{"id":"ok","text":"Next"},{"id":"cancel","text":"Cancel"}],"showOnLoad":false,"focusOnLoad":false,"postbackOnClose":true,"postbackOnResize":false,"postbackOnCancel":true,"maintainPostbackVisibility":true,"controlId":"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset","contentElementId":"floatingwindowContent_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset","selectedTabHiddenFieldId":"floatingwindowTab_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset","visibilityStateHiddenFieldId":"floatingwindowVisible_UploadAsset_espr_renderHost_PageStructureDisplayRenderer_esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e_ctlAssetManager_flwBrowseAssets_ctrlUploadAsset"}',
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$cKeywords$txtKeywords":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$consoleMessagePanel$hfState":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$console$resultsPerPageControl$ddlRecords":"10",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$notificationPanel$hfState":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_ee106874-da19-4ca0-8692-7d6ae7374ced$cContainer$txtText":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_1080c401-24c8-44cb-97f7-5014d46a3a42$cContainer$txtText":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_24bc0b1e-cf59-4998-9aa7-8c4202b84087$cContainer$txtText":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_d1ba2900-a1ef-40e7-a2fb-88183d9afbc8$cContainer$txtText":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_dded97bb-9ebd-44ad-bde5-194d553e68cf$cContainer$TextArea":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_6e4ad32c-2ea2-467f-898a-aab615387810$cContainer$DatePickerField$txtDate":"20/06/2018",
"espr$renderHost$PageStructureDisplayRenderer$esctl_9eeec701-7104-42d2-9149-394fa9c2cc25$ctl00$InnerRenderer_9eeec701-7104-42d2-9149-394fa9c2cc25$esctl_d1575fa2-5423-45f4-b662-116d9c23467d$ctl00$InnerRenderer_d1575fa2-5423-45f4-b662-116d9c23467d$esctl_57f6b989-c51a-4e3b-9d18-c941d0e259f4$formBuilderUI$fieldset$formBuilderStructureInputRendererHost$FormBuilderStructureInputRenderer$esctl_6e4ad32c-2ea2-467f-898a-aab615387810$cContainer$DatePickerField$hfInitialDate":"20/06/2018",
"g-recaptcha-response":"",
"__VIEWSTATEGENERATOR":"2362A2C6",
"__EVENTVALIDATION":"/wEdADUT0XeWrvGw8DZUCDYiHUdAxJMl82VmbJPmhJ8RpBZ23vw12ex4WxOx+EKxvDyp2IrEGisIDESiFFMN8gWfSyLQEPnj3/6iNzxs+I1ATengOejQvdzSnFI2RGbtk7fv2LTzUY68prbuXNaHDYez9qIN1cI7MV+unCUFbdSklmB38ayX438Re7MB+bS+c7dposM5nyvdUMTFHWhhiKLon/wrSj9X1amNHUlZ3p47XyAIXFh2E4f6LvTk10rZSI/PaHBkO5zw7SOPoL2HzvfUh5NNodVBz8MQ1fyAaGEN+aeNIw7tBSn1c7dzq2iHUrQIYgvnryclOnjrzlrKiHngCm7QhDkhbAak4aonopvvFKRcQ3cQhpD2EBAZyNQO/HcM4gfSXfemvXUSz1vm7CNQ/WOsEiEIBkkSDrgkwaaDuOJWkMNnyTQ6C6MdK+D4AxdbF6aN4wOJab/at+mh+ADCrj5IKH+O0o6GMmFR5r3kydcIFjyrA1o9zjuBBvKSRrFW7gxd+8jIloTRE9IvQBO4Qlex9CzRZYdLp8kplIywhM21vejxxB/kSYdIduq1jRqaaqPpb3ZmeJJ3RTeqrmgAE6LMqqw5yA9dmxGpjDDaxjnRj0UzZhdbU/z4ml1sDtgR/x236w0deW4gRHcU+rnabSoil4cjL/g6Zk8za6XPzIFKe1XXVXvEmjEO4N3VEUZt/SLZ8LaB+WIxdX3cBgS9afcrW7D68Bh1ygziP97i6m94/z//N4EdiIGs0VQZJM84zge8yJVeLLtIVJk7+/ix/1wBJxuScNaYIXpMDeWu2wfOZq4zNDct2trm8wM/qcNwDVJYXRGKamGx7gEM2nkqJEnzJ/Ua+d8Qvn81v+t00X+godIYhr2qpafnIgEuFIVaQ1HIrQOWDMZV9qv5C494Kh6eVZ2YwbutYIvp8wuHMs/la2Sp2kfbDK38ZmzdvbyzOelmADOiNdatB8W+agBiGYJ0uHPQ72IK/LD+SieKzysQF7gbGRw2aI93uK4vcAUIbc1/xoEzRhxEZ1Bl6KpyTbPqVohDLgjPj5/sMAib6/++0fxbBWdl1z3Q9BFXN5+vhqAz1j6V0pqFx84EKT8wddMMSXG1r+KxF2+98SBtkTLkFwsAx36wtSioO6Y2eWnYcNqykzVGxUc/dq41P0ZIBhvd",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset$ctnBinaryUpload$tabBinaryUpload$notificationPanel$hfState":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset$ctnBinaryUpload$tabBinaryUpload$pnlBinaryUpload$sbumBinary$state":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset$ctnBinaryUpload$tabContentUpload$notificationPanel$hfState":"",
"espr$renderHost$PageStructureDisplayRenderer$esctl_5dd14cab-2d7b-4ac6-b092-333495d8835e$ctlAssetManager$flwBrowseAssets$ctrlUploadAsset$flwUploadAsset$ctnBinaryUpload$ctnBinaryUpload_SelectedTabHiddenField":"0"}


#### READ HTML 1.0

html = requests.post(url, data=year_d, cookies=year_cookies)
soup = BeautifulSoup(html.text, 'lxml')


#### SCRAPE DATA

links = soup.find('table', 'grid grid-console').find_all('td', 'title title')
for link in links:
    file_name = link.find('a', href=True).text
    if '.csv' in file_name:
        post_back = link.find('a', href=True)['href'].split("doPostBack('")[-1].split("',")[0]
        file_d['__EVENTTARGET'] = post_back
        file_html = requests.post(url, data=file_d, cookies=year_cookies)
        if file_html.status_code == 200:
            file_num = post_back.split('_')[-1]
            url = 'https://www.chelmsford.gov.uk/_resources/assets/attachment/full/0/{}.csv'.format(file_num)
            csvMth = file_name.split('for')[-1].strip()[:3]
            csvYr = '20'+file_name.split('.csv')[0].strip()[-2:]
            if 'Apr-Jun' in file_name:
                csvMth = 'Q2'
            if 'Jan-Mar' in file_name:
                csvMth = 'Q1'
            if 'Jul-Sep' in file_name:
                csvMth = 'Q3'
            if 'Oct-Dec' in file_name:
                csvMth = 'Q4'
            csvMth = convert_mth_strings(csvMth.upper())
            data.append([csvYr, csvMth, url])


#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF
