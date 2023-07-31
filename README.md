# ghub-utils
A collection of ipywidgets and scripts adapted to the Ghub tool creation process.

### Adding to other Projects
<p>Still a work-in-progress project that isn't a standalone Python package, therefore to make use of the code found here 
this repository must be added as a git [submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) to an existing git repository. 
Suppose your project <em>awesome-proj</em> is located in <code>~/the/path/to/my/awesome-proj</code>:<br>
<ol>
  <li>switch to your project's main directory: <em>eg (bash)</em><code>$ cd ~/the/path/to/my/awesome-proj</code></li>
  <li>add the submodule: <code>$ git submodule add git@github.com:GhubGateway/ghub-utils.git</code></li>
</ol>
</p>

<p>To import <code>ghub-utils.ghub\_utils</code> inside your project, its absolute path must first be added to your Python Path. To do that you must first locate your environment's Python <code>site-packages</code> folder:
<ul>
  <li>
  inside any Python instance, run the following code:<br>
    <code>import site</code><br>
    <code>site.getusersitepackages()</code><br>
  The path will look similar to: <code>/home/user/anaconda3/envs/some\_env/lib/python3.7/site-packages</code>
  </li>
</ul>
</p>

<p>Next copy the path file <code>ghub-utils/ghub\_utils.pth</code> into the site-packages folder.</p>

<p>Finally locate the absolute path to your project's <code>ghub-utils</code> directory <code>path/to/your/project/ghub-utils</code> and copy into <code>site-packages/ghub\_utils.pth</code></p>.

<p><code>ghub-utils/ghub\_utils</code> is now ready to be imported and used as any package.</p>

### Updating ghub-utils
<p>
The ghub-utils submodule can be updated at any time like any other git repository:
<ol>
  <li><code>$ cd path/to/your/project/ghub-utils/</code></li>
  <li><code>$ git pull</code></li>
</ol>
</p>

### Cloning Repositories with Submodules
<p>NOTE: when cloning repositories from github with an existing submodule, remember to add the flag <code>--recursive</code>, eg. <code>git clone git@github.com:ruskirin/initmip-cluster.git --recursive</code>. For full solutions see: [https://stackoverflow.com/q/11358082](https://stackoverflow.com/q/11358082)</p>
