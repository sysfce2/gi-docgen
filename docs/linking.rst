=====================
Linking items by name
=====================

Gi-docgen is capable of linking symbols across the same introspected namespace,
by using a qualifier fragment and the symbol name.

For instance:

::

    /**
     * ExampleFoo:
     *
     * This structure is related to [struct@Bar].
     */

    /**
     * example_foo_set_bar:
     *
     * Sets [struct@Example.Bar] on an instance of `Foo`.
     */

    /**
     * ExampleFoo:bar:
     *
     * Sets an instance of [`Bar`](struct.Bar.html) on `Foo`.
     */

will all link to `Bar`.

Backticks will be stripped, so `[\`class@Foo\`]` will correctly link to `Foo`.

The link can either be a fully qualified name, which includes the namespace; or
a name relative to the current names; for instance, both of the following links
will point to `ExampleFoo` when generating the documentation for the "Example"
namespace:

- `[class@Foo]`
- `[class@Example.Foo]`

The available qualifier fragments are:

+------------+--------------------------+-----------------------------------------+
| Fragment   | Description              | Example                                 |
+============+==========================+=========================================+
| `alias`    | An alias to another type | `[alias@Allocation]`                    |
+------------+--------------------------+-----------------------------------------+
| `class`    | A GObject class          | `[class@Widget]`, `[class@Gdk.Surface]` |
+------------+--------------------------+-----------------------------------------+
| `const`    | A constant symbol        | `[const@Gdk.KEY_q]`                     |
+------------+--------------------------+-----------------------------------------+
| `ctor`     | A constructor function   | `[ctor@Gtk.Box.new]`                    |
+------------+--------------------------+-----------------------------------------+
| `enum`     | An enumeration           | `[enum@Orientation]`                    |
+------------+--------------------------+-----------------------------------------+
| `error`    | A `GError` domain        | `[error@Gtk.BuilderParseError]`         |
+------------+--------------------------+-----------------------------------------+
| `flags`    | A bitfield               | `[flags@Gdk.ModifierType]`              |
+------------+--------------------------+-----------------------------------------+
| `func`     | A global function        | `[func@Gtk.init]`, `[func@show_uri]`    |
+------------+--------------------------+-----------------------------------------+
| `iface`    | A GTypeInterface         | `[iface@Gtk.Buildable]`                 |
+------------+--------------------------+-----------------------------------------+
| `method`   | An instance method       | `[method@Gtk.Widget.show]`              |
+------------+--------------------------+-----------------------------------------+
| `property` | A GObject property       | `[property@Gtk.Orientable:orientation]` |
+------------+--------------------------+-----------------------------------------+
| `signal`   | A GObject signal         | `[signal@Gtk.RecentManager::changed]`   |
+------------+--------------------------+-----------------------------------------+
| `struct`   | A C structure            | `[struct@Gtk.TextIter]`                 |
+------------+--------------------------+-----------------------------------------+
| `vfunc`    | A virtual function       | `[vfunc@Gtk.Widget.measure]`            |
+------------+--------------------------+-----------------------------------------+

Additionally, the `id` fragment, followed by a C symbol identifier, will try to link to the function; for instance:

::

    // Equivalent to [func@Gtk.show_uri], will link to gtk_show_uri()
    [id@gtk_show_uri]

    // Equivalent to [method@Gtk.Widget.show], will link to gtk_widget_show()
    [id@gtk_widget_show]

The `id` fragment can only be used for symbols within the current namespace.