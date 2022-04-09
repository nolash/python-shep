from shep.state import State


# we don't like "NEW" as the default label for a new item in the queue, so we change it to BACKLOG
State.set_default_state('backlog')

# define all the valid states
st = State(5)
st.add('pending')
st.add('blocked')
st.add('doing')
st.add('review')
st.add('finished')

# define a couple of states that give a bit more context to progress; something is blocked before starting development or something is blocked during development...
st.alias('startblock', st.BLOCKED, st.PENDING)
st.alias('doingblock', st.BLOCKED, st.DOING)


# create the foo key which will forever languish in backlog
k = 'foo'
st.put(k)
foo_state = st.state(k)
foo_state_name = st.name(foo_state)
foo_contents_r = st.get('foo')
print('{} {} {}'.format(k, foo_state_name, foo_contents_r))


# Create bar->baz and advance it from backlog to pending
k = 'bar'
bar_contents = 'baz'
st.put(k, contents=bar_contents)

st.next(k)
bar_state = st.state(k)
bar_state_name = st.name(bar_state)
bar_contents_r = st.get('bar')
print('{} {} {}'.format(k, bar_state_name, bar_contents_r))

# Create inky->pinky and move to doing then doing-blocked
k = 'inky'
inky_contents = 'pinky'
st.put(k, contents=inky_contents)
inky_state = st.state(k)
st.move(k, st.DOING)
st.set(k, st.BLOCKED)
inky_state = st.state(k)
inky_state_name = st.name(inky_state)
inky_contents_r = st.get('inky')
print('{} {} {}'.format(k, inky_state_name, bar_contents_r))

# then replace the content
# note that replace could potentially mean some VCS below
inky_new_contents = 'blinky'
st.replace(k, inky_new_contents)
inky_contents_r = st.get('inky')
print('{} {} {}'.format(k, inky_state_name, inky_contents_r))

# so now move to review
st.move(k, st.REVIEW)
inky_state = st.state(k)
inky_state_name = st.name(inky_state)
print('{} {} {}'.format(k, inky_state_name, inky_contents_r))

