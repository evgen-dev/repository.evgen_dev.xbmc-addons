<?php

$plugin_dirs = glob('repo/*');

foreach($plugin_dirs as $dir){
	$plugin_zips = glob($dir.'/*.zip');
	foreach($plugin_zips as $zip){
		file_put_contents($zip.'.md5', md5_file($zip));
		echo "Make $zip.md5\n";
	}
}

echo 'done';