// leave at least 2 line with only a star on it below, or doc generation fails
/**
 *
 *
 * Placeholder for custom user javascript
 * mainly to be overridden in profile/static/custom/custom.js
 * This will always be an empty file in IPython
 *
 * User could add any javascript in the `profile/static/custom/custom.js` file
 * (and should create it if it does not exist).
 * It will be executed by the ipython notebook at load time.
 *
 * Same thing with `profile/static/custom/custom.css` to inject custom css into the notebook.
 *
 * Example :
 *
 * Create a custom button in toolbar that execute `%qtconsole` in kernel
 * and hence open a qtconsole attached to the same kernel as the current notebook
 *
 *    $([IPython.events]).on('app_initialized.NotebookApp', function(){
 *        IPython.toolbar.add_buttons_group([
 *            {
 *                 'label'   : 'run qtconsole',
 *                 'icon'    : 'icon-terminal', // select your icon from http://fortawesome.github.io/Font-Awesome/icons
 *                 'callback': function () {
 *                     IPython.notebook.kernel.execute('%qtconsole')
 *                 }
 *            }
 *            // add more button here if needed.
 *            ]);
 *    });
 *
 * Example :
 *
 *  Use `jQuery.getScript(url [, success(script, textStatus, jqXHR)] );`
 *  to load custom script into the notebook.
 *
 *    // to load the metadata ui extension example.
 *    $.getScript('/static/notebook/js/celltoolbarpresets/example.js');
 *    // or
 *    // to load the metadata ui extension to control slideshow mode / reveal js for nbconvert
 *    $.getScript('/static/notebook/js/celltoolbarpresets/slideshow.js');
 *
 *
 * @module IPython
 * @namespace IPython
 * @class customjs
 * @static
 */

var currenth1=0;
 
function regentoc() {
document.getElementById("toc").innerHTML = "";
var currenth1 = 0;
$("h1,h2").not(document.getElementById("toctitle")).each(function(mainIndex) {
    el = $(this);
    title = el.attr("id");
    text = el.html();
    link = "#" + el.attr("id");
    if ( document.getElementById(title).tagName == "H1" ) {
        currenth1 += 1;
        newLine =
            "<li class='maintoc'>" +
                currenth1 + " " +
                "<a href='" + link + "'>" + text + "</a>" +
            "</li>" +
            "<ul id='h1" + currenth1 + "'></ul>";
        document.getElementById("toc").innerHTML += newLine;
    } else if ( document.getElementById(title).tagName=="H2" ) {
        h1list = document.getElementById("h1"+currenth1);
        newLine = "<li class='subtoc'>" + "<a href='" + link + "'>" + text + "</a>" + "</li>";
        h1list.innerHTML += newLine;
    }
});
}
 
setInterval(regentoc,1000);


if (IPython.CodeCell) {
  IPython.CodeCell.options_default.cm_config.autoCloseBrackets = false;
}

// Hide header and toolbar by default
$([IPython.events]).on("app_initialized.NotebookApp", function () {
    $('div#header-container').hide();
    $('div#maintoolbar').hide();
});

// Notebook extensions
$([IPython.events]).on('app_initialized.NotebookApp', function(){
    //require(['/static/custom/hierarchical_collapse.js']);
    require(['/static/custom/codefolding/codefolding.js'])
})
