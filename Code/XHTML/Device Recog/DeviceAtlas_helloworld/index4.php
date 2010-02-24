<?php
header ("Cache-Control: max-age=200 ");
header ("Content-Type: application/xhtml+xml ");
require_once 'da_api.php';
$tree = da_get_tree_from_file('json/DeviceAtlas.json');
$ua = $_SERVER['HTTP_USER_AGENT'];
echo '<?xml version="1.0" encoding="utf-8"?>';
?>
<!DOCTYPE html PUBLIC "-//WAPFORUM//DTD XHTML Mobile 1.2//EN"
"http://www.openmobilealliance.org/tech/DTD/xhtml-mobile12.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" >
<head>
    <title>Hello Mobile World</title>
    <style type="text/css">
    	h1 {background-color: #000000; color: #ffffff;}
    	li {list-style: none;}
    	.property {font-weight: bold;}
    </style>
</head>
<body>
	<p>
        <img id="logo" src="img/logo_128x57.png" alt="dotMobi Logo" width="128" height="57"/>
    </p>
	<hr />
    <h1>Hello <?php echo da_get_property($tree, $ua, 'vendor');?> user!</h1>
    <ul>
		<?php foreach(da_get_properties($tree, $ua) as $name => $value): ?>
        <li><span class="property"><?php echo $name?>: </span><?php echo $value?></li>
		<?php endforeach; ?>
    </ul>
</body>
</html>