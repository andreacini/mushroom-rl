import logging


class Core(object):
    """
    Implements the functions to run a generic algorithm.
    """
    def __init__(self, agent, mdp):
        """
        Constructor.

        # Arguments
            agent (object): the agent moving according to a policy.
            mdp (object): the environment in which the agent moves.
            params (dict): other params.
        """
        self.agent = agent
        self.mdp = mdp

        self.agent.initialize(self.mdp.get_info())

        self.logger = logging.getLogger('logger')

        self._state = self.mdp.reset()
        self._dataset = list()
        self._episode_steps = 0

    def learn(self, n_iterations, how_many, n_fit_steps, iterate_over,
              render=False):
        """
        This function is used to learn a policy. An iteration of the loop
        consists in collecting a dataset and fitting the agent's Q-function
        approximator on that. Multiple iterations can be done in order to append
        new samples to the dataset using the newly learned policies. This
        function generalizes the learning procedure of online and batch
        algorithms.

        # Arguments
            n_iterations (int > 0): number of iterations.
            how_many (int > 0): number of samples or episodes to collect in a
                single iteration of the loop.
            n_fit_steps (int > 0): number of fitting steps of the learning
                algorithm.
            iterate_over (string): whether to collect samples or episodes in a
                single iteration of the loop.
            render (bool): whether to render the environment or not.
        """
        assert iterate_over == 'samples' or iterate_over == 'episodes'

        for self.iteration in xrange(n_iterations):
            self.logger.info('Iteration %d' % self.iteration)

            self.logger.debug('Moving for %d %s...' % (how_many, iterate_over))
            self.move(how_many, iterate_over, collect=True, render=render)

            self.logger.debug('Fitting for %d steps...' % n_fit_steps)
            self.agent.fit(self._dataset, n_fit_steps)

    def evaluate(self, initial_states, render=False):
        """
        This function is used to evaluate the learned policy.

        # Arguments
            initial_states (np.array): the array of initial states from where to
                start the evaluation episodes. An evaluation episode is run for
                each state.
            render (bool): whether to render the environment or not.
        """
        for i in xrange(initial_states.shape[0]):
            self._state = self.mdp.reset(initial_states[i, :])
            self.move(1, iterate_over='episodes', collect=True, render=render)

    def move(self,
             how_many,
             iterate_over,
             collect=False,
             render=False):
        """
        Move the agent.

        # Arguments
            how_many (int > 0): number of samples or episodes to collect.
            iterate_over (string): whether to collect samples or episodes.
            collect (bool): whether to store the collected data or not.
            render (bool): whether to render the environment or not.

        # Returns
            The list of discounted rewards obtained in each episode.
        """
        if iterate_over == 'episodes':
            i = 0
            self._episode_steps = 0
            while i < how_many:
                while not self._step(collect, render):
                    continue
                self._state = self.mdp.reset()
                self._episode_steps = 0
                i += 1
        else:
            i = 0
            while i < how_many:
                if self._step(collect, render):
                    self._state = self.mdp.reset()
                    self._episode_steps = 0
                i += 1

    def _step(self, collect, render):
        action = self.agent.draw_action(self._state)
        next_state, reward, absorbing, _ = self.mdp.step(action[0])
        self._episode_steps += 1

        if render:
            self.mdp.render()

        last = not(self._episode_steps < self.mdp.horizon and not absorbing)
        sample = (self._state, action, reward, next_state, absorbing,
                  last)

        self.logger.debug(sample[:-1])

        if collect:
            self._dataset.append(sample)

        self._state = next_state

        return last

    def get_dataset(self):
        """
        # Returns
            The dataset.
        """
        return self._dataset

    def reset_dataset(self):
        """
        Reset the stored dataset list.
        """
        self._dataset = list()
