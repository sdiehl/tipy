tipy
====

Preprocessor for Python interactive shell sessions.

Turns this:

```python
x = 3
y = 4
>>> print x + y
```

Into this:

```pycon
>>> x + y
7
```

Which renders into html:

```html
<div class="highlight">
    <pre>
        <span class="gp">&gt;&gt;&gt;</span>
        <span class="k">print</span>
        <span class="n">x</span>
        <span class="o">+</span>
        <span class="n">y</span>
        <span class="go">7</span>
    </pre>
</div>
```

Or to LaTeX:

```pycon
\begin{Verbatim}[commandchars=\\\{\}]
\PY{g+gp}{\PYZgt{}\PYZgt{}\PYZgt{} }\PY{k}{print} \PY{n}{x} \PY{o}{+} \PY{n}{y}
\PY{g+go}{7}
\end{Verbatim}
```

Goal is to build a Python shell preprocessor that can integrate
with the the pandoc ecosystem for building Python tutorials
portable to any format.
