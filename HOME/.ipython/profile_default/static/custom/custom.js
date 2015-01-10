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

 $([IPython.events]).on('app_initialized.NotebookApp', function(){
     IPython.toolbar.add_buttons_group([
         {
              'label'   : 'run qtconsole',
              'icon'    : 'icon-terminal', // select your icon from http://fortawesome.github.io/Font-Awesome/icons
              'callback': function () {
                  IPython.notebook.kernel.execute('%qtconsole')
              }
         }
         // add more button here if needed.
         ]);
 });

function load_vimception() {
    cell = IPython.notebook.insert_cell_at_index('code', 0);
    IPython.notebook.select(0);
    cell.set_text('%load_ext vimception\n%reload_ext vimception\n%vimception');
    if (!IPython.notebook.kernel) {
        $([IPython.events]).on('status_started.Kernel', function() {
            cell.execute();
            IPython.notebook.delete_cell();
        });
    } else { 
        cell.execute();
        IPython.notebook.delete_cell();
    }
}

$([IPython.events]).on('notebook_loaded.Notebook', function(){
    $('#help_menu').prepend([
            '<li id="vimception" title="load up vimception cell">',
            '<a href="#" title="vimception" onClick="load_vimception()">vimception</a></li>',
            '<li id="reflow" title="reflow markdown text">',
            '<a href="#" title="vimception" onClick="reflow_markdown()">reflow text</a></li>',
            ].join("\n"));

// uncomment next line to *always* start in vimception
// $('#vimception a').click();
});

if (IPython.CodeCell) {
  IPython.CodeCell.options_default.cm_config.autoCloseBrackets = false;
}

// Hide header and toolbar by default
$([IPython.events]).on("app_initialized.NotebookApp", function () {
        $('div#header').hide();
            $('div#maintoolbar').hide();
});

// Notebook extensions
$([IPython.events]).on('app_initialized.NotebookApp', function(){
    //require(['/static/custom/hierarchical_collapse.js']);
    require(['/static/custom/codefolding/codefolding.js'])
})
