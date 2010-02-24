<?php echo '<?xml version="1.0" encoding="UTF-8"?>'?>
<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.1//EN" "http://www.openmobilealliance.org/tech/DTD/xhtml-mobile11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<link rel="stylesheet" href="style.css" type="text/css" media="all" />
		<meta http-equiv="content-type" content="text/html; charset=utf-8" />
		<META http-equiv="cache-control" content="no-cache">
		<script type="text/javascript" src="majax.js"></script>
		<title>dev.mobi mAjax</title>
	</head>
	<body>

		<div>
			<a href="fallbackTime.php?uid=<?php echo uniqid(); ?>" onclick="return updateElm('getTime.php', 'timeDiv');" >Get server time</a>
			<div id='timeDiv'><?php echo date('l dS \of F Y h:i:s A'); ?></div>
		</div>
	</body>
</html>
