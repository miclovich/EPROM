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
    <?php
            if(da_get_property($tree, $ua, 'image.Png')): //Supports PNG images
            	if(da_get_property($tree, $ua, displayWidth) >= 240){
            		$image = 'logo_239x107.png';
            		$width = 239;
            		$height = 107;
            	} else {
            		$image = 'logo_128x57.png';
            		$width = 128;
            		$height = 57;
            	}
    ?>
	<p>
        <img id="logo" src="img/<?php echo $image; ?>" alt="dotMobi Logo" width="<?php echo $width; ?>" height="<?php echo $height; ?>"/>
    </p>
    <?php   endif; ?>
	<hr />
    <h1>Hello <?php echo da_get_property($tree, $ua, 'vendor');?> user!</h1>
    <ul>
        <li><a href="index.php?page=1" accesskey="1">(1) Link 1</a></li>
        <li><a href="index.php?page=2" accesskey="2">(2) Link 2</a></li>
        <li><a href="index.php?page=3" accesskey="3">(3) Link 3</a></li>
    </ul>
    <p>Lorem ipsum dolor sit amet, consectetuer adipiscing elit. 
    In euismod mi a urna. In ultrices turpis vitae nibh.</p>
    <p>Sed sed ipsum id dolor nonummy dignissim. Nulla mi ante, 
    placerat nec, vestibulum sed, fringilla at, velit.</p>
    <p>Nulla nonummy purus sed nisl. Mauris tincidunt urna sit amet dui. 
    Cras sem justo, mollis et, tincidunt a, pellentesque eget, quam. 
    Vestibulum quis velit et erat dictum ultrices. 
    Praesent fermentum arcu nec sapien. Nunc eleifend.</p>
</body>
</html>