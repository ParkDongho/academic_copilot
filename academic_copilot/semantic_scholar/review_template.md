
```dataview
table without id title + "<sup>" + (total_citation + "") + "</sup><br>" + subtitle + "<br><br>" + tldr as "Overview"
where file.name = this.file.name
```

```dataview
Table WITHOUT ID title,
  link("20_Work/Projects/PaperReader/en_kr/" + regexreplace(regexreplace(original, "^/|/$", ""), "/", "-") + "/zh", "kr") as KR,
  link("20_Work/Projects/PaperReader/en_kr/" + regexreplace(regexreplace(original, "^/|/$", ""), "/", "-") + "/en", "en") as EN,
  "[doi.org](https://doi.org/" + doi + ")" as Link,
  "[slide](http://localhost:8080/posts/semantic/" + key+ ".md)" as Slide
where file.name = this.file.name
```

-------

<!-- graphical abstract -->

$(graphical_abstract)

<!-- graphical abstract -->

-------

<!-- review -->

$(review)

<!-- review -->

-------

<!-- bibliography -->

$(bibliography)

<!-- bibliography -->


