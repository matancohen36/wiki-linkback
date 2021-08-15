Wiki Link-Back
In this exercise you will write a computer program that receives a URL to a Wikipedia article on the command line.  The program will print a list of URLs to other Wikipedia articles that are linked to from the original article, and also link back to it.

For example, if we use the article about Israel

   $ python my-program.py https://en.wikipedia.org/wiki/Israel

We expect that the link to the article about Theodor Herzl will be among the results.
However (at least at the time of writing this), the Israel article links to the Iron Age article, but the Iron Age article does not link back to Israel.


To summarize, a correct program will print the link to the Theodor Herzl article, but not the link to the Iron Age article.
You may only use modules in the Python standard library.

bonus: parallelize your program so that it completes faster.
