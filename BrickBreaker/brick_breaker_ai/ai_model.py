import torch
import torch.nn as nn
import torch.optim as optim

class AIModel(nn.Module):
    def __init__(self, state_size, action_size, learning_rate=0.001):
        super(AIModel, self).__init__()
        self.fc1 = nn.Linear(state_size, 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, action_size)
        self.optimizer = optim.Adam(self.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()

    def forward(self, state):
        x = torch.relu(self.fc1(state))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

    def predict(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            return torch.argmax(self.forward(state)).item()

    def train(self, batch, gamma):
        states, actions, rewards, next_states, dones = batch
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)

        q_values = self.forward(states)
        next_q_values = self.forward(next_states).max(1)[0]

        target_q_values = rewards + (1 - dones) * gamma * next_q_values
        q_values = q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        loss = self.loss_fn(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def save_model(self, path):
        torch.save(self.state_dict(), path)

    @staticmethod
    def load_model(path, state_size, action_size):
        model = AIModel(state_size, action_size)
        model.load_state_dict(torch.load(path))
        return model
