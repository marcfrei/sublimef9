# Copyright (c) 1994 - 2014 Oberon microsystems, Inc., Switzerland.

import sublime, sublime_plugin

view_b = None

def next_char_pos(view, i, j):
	while (i != j) and (view.substr(i) <= ' '):
		i += 1
	return i

def next_char(view, i, j):
	k = next_char_pos(view, i, j)
	if k == j:
		c = 0
	else:
		c = view.substr(k)
		k += 1
	return c, k

def diff(view_a, na, ja, da, view_b, nb, ib, jb, j, d, s, n):
	ja = da
	if ja != na:
		s[0], ka = next_char(view_a, ja, na)
		da = ka;
		i = 1
		while i != n:
			s[i], ka = next_char(view_a, ka, na)
			i += 1
		i = 0
		kb = ib
		while (j != n) and (i != d) and (kb != nb):
			jb = kb
			cb, kb = next_char(view_b, kb, nb)
			if cb == s[0]:
				p = kb
				j = 0
				while (j != n) and (cb == s[j]):
					cb, kb = next_char(view_b, kb, nb)
					j += 1
				kb = p
			i += 1
	return ja, da, jb, j

def compare_views(view_a, pos_a, view_b, pos_b):
	na = view_a.size()
	nb = view_b.size()
	ia = next_char_pos(view_a, pos_a, na)
	ib = next_char_pos(view_b, pos_b, nb)
	while (ia != na) and (ib != nb) and (view_a.substr(ia) == view_b.substr(ib)):
		ia = next_char_pos(view_a, ia + 1, na)
		ib = next_char_pos(view_b, ib + 1, nb)
	da = ja = ka = ia if ia == na else ia + 1
	db = jb = kb = ib if ib == nb else ib + 1
	d = 1
	j = 0
	n = 32
	s = [0] * n
	while (j != n) and ((ja != na) or (jb != nb)):
		ja, da, jb, j = diff(view_a, na, ja, da, view_b, nb, ib, jb, j, d, s, n)
		d += 1
		if j != n:
			jb, db, ja, j = diff(view_b, nb, jb, db, view_a, na, ia, ja, j, d, s, n)
	ra = sublime.Region(ia, ja)
	rb = sublime.Region(ib, jb)
	return ra, rb

class DeactivationListener(sublime_plugin.EventListener):
	def on_deactivated(self, view):
		global view_b
		view_b = view

	def on_close(self, view):
		global view_b
		if view == view_b:
			view_b = None

class SublimeF9Command(sublime_plugin.TextCommand):
	def run(self, edit):
		view_a = self.view
		if (view_a != view_b) and (view_b is not None):
			sa = view_a.sel()
			sb = view_b.sel()
			if sa and sb:
				ra, rb = compare_views(
					view_a, max(sa[0].a, sa[0].b),
					view_b, max(sb[0].a, sb[0].b))
				sb.clear()
				sa.clear()
				sb.add(rb)
				sa.add(ra)
				view_b.show_at_center(min(rb.a, rb.b))
				view_a.show_at_center(min(ra.a, ra.b))
				view_b.window().focus_view(view_b)
				view_a.window().focus_view(view_a)
