var req;

function getXHR()
{
	if(window.XMLHttpRequest) {
		req = new XMLHttpRequest();
		return true;
	}
	else try {
		req = new ActiveXObject('Msxml2.XMLHTTP');
		return true;
	} catch(e) {
		try {
			req = new ActiveXObject("Microsoft.XMLHTTP");
			return true;
		} catch(e) {
			req = false;
			return false;
		}
	}
}

function updateElm(url, id)
{
	if(getXHR())
	{
		req.open('POST', url, true);
		req.onreadystatechange = function()
		{
			if(req.readyState == 4) {
				if(req.status == 200) {
					document.getElementById(id).innerHTML = req.responseText;
				}
			} 
		}
		req.send('');
	}
	else return true;
	return false;
}


