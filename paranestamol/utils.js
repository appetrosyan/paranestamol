function baseName(str)
{
	var base = new String(str).substring(str.lastIndexOf('/') + 1);
	if(base.lastIndexOf(".") != -1)
		base = base.substring(0, base.lastIndexOf("."));
	return base;

}


function loadFile(url, mdl)
{
	var path=(displayBridge.loadSamples(url))
	mdl.append(
		{
			'url': path,
			'name': baseName(path),
			'legend': baseName(path),
			'display': true,
			'color': "#ff0000"
		})
	displayBridge.loadSamplesCallback(baseName(path))
}

var prettyTypes = {
	'lower': qsTr("Lower"),
	'diagonal': qsTr("Diagonal")
}
