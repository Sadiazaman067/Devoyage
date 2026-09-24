# models/ -- Sadia's package. Database access only.
#
# Rule from the project spec: models never import Kivy, and views never touch
# the database directly. Every function here takes a sqlite3 connection as its
# first argument -- controllers own the connection lifecycle, models just use it.
