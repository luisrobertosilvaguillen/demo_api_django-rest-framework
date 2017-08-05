from __future__ import absolute_import

# from celery import shared_task


# @shared_task
# def Render_Mail(Subject, To, Body, From = "info@negociosexchange.com", Cc=""):
# 	Url_Sistema = "#"
# 	html = '<html lang="es-ES"><head><meta charset="utf-8"></head><body><div style="background:#f0f0f0;margin:0;padding:10px 0" bgcolor="#f0f0f0"><br><table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0" bgcolor="#f0f0f0"><tbody><tr><td align="center" valign="top" bgcolor="#f0f0f0" style="background:#f0f0f0"><table width="600" cellpadding="0" cellspacing="0" border="0" class="m_-6520767629608970887container" bgcolor="#ffffff" style="border-bottom-color:#e0e0e0;border-bottom-style:solid;border-bottom-width:1px;color:#162e34;font-family:Helvetica,Verdana,sans-serif"><tbody><tr><td class="m_-6520767629608970887header" style="border-left-color:#e0e0e0;border-left-style:solid;border-left-width:1px"><div style="background:#162e34;border:1px solid #162e34;border-radius:2px;height:5px">&nbsp;</div></td></tr><tr><td class="m_-6520767629608970887logo" style="border-bottom-color:#efefef;border-bottom-style:solid;border-bottom-width:1px;border-left-color:#e0e0e0;border-left-style:solid;border-left-width:1px;padding:15px 0;text-align:center" align="center"><img src="http://iffdev.com/nexchange/assets/img/nexchange.png" width="238" height="180" alt="" class="CToWUd"></td></tr><tr><td class="m_-6520767629608970887container-padding" bgcolor="#ffffff" style="background:#ffffff;border-left-color:#e0e0e0;border-left-style:solid;border-left-width:1px;padding-left:30px;padding-right:30px"><br>'+	Body+'</td></tr><tr><td style="border-left-color:#e0e0e0;border-left-style:solid;border-left-width:1px"><table border="0" width="100%" height="100%" cellpadding="0" cellspacing="0" bgcolor="#fbfbfb" class="m_-6520767629608970887footer" style="border-top-color:#efefef;border-top-style:solid;border-top-width:1px;height:69px;width:100%"><tbody><tr> <td class="m_-6520767629608970887social" style="border-left-color:#e0e0e0;border-left-style:none;border-left-width:1px;color:#434343;font-size:12px;line-height:20px;text-align:center;vertical-align:middle;width:60%" align="center" valign="middle">Ingresar Al Sistema: &nbsp; <a href="'+Url_Sistema+'"> Sistema</a> &nbsp;</td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table><br></div></body></html>'
# 	import requests
# 	requests.post(	
# 	 "https://api.mailgun.net/v3/sistema-ac.com/messages",
# 	 verify=False,
# 	 auth=("api", "key-83bba8a17bf83f1f4f2582cd7dfb1c8e"),
# 	 data={"from": From,
# 	       "to": [To],
# 	       "subject": Subject,
# 	       "html": html})