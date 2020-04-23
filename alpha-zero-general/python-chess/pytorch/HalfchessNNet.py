import sys
sys.path.append('..')
from utils import *

import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.autograd import Variable

class SExBlock(nn.Module):
	def __init__(self, in_channels, r):
		super(SExBlock, self).__init__()
		self.se = nn.Sequential(
			GlobalAvgPool(),
			nn.Linear(in_channels, in_channels//r),
			nn.ReLU(inplace=True),
			nn.Linear(in_channels//r, in_channels),
			nn.Sigmoid()
			)
	def forward(self, x):
		se_weight = self.se(x).unsqueeze(-1).unsqueeze(-1)
		return x.mul(se_weight)
class GlobalAvgPool(nn.Module):
	def __init__(self):
		super(GlobalAvgPool, self).__init__()
	def forward(self, x):
		return x.view(*(x.shape[:-2]),-1).mean(-1)

class ResidualBlock(nn.Module):
	def __init__(self, channels):
		super(ResidualBlock, self).__init__()
		self.channels = channels
		self.blocks = nn.Sequential(
			nn.Conv2d(self.channels, self.channels, 3, stride=1, padding=1),
			nn.BatchNorm2d(self.channels),
			nn.ReLU(inplace=True),
			nn.Conv2d(self.channels, self.channels, 3, stride=1, padding=1),
			nn.BatchNorm2d(self.channels),
			)

	def forward(self, x):
		residual = x
		x = self.blocks(x)
		x += residual
		return F.relu(x, inplace=True)

class HalfchessNNet(nn.Module):

	def __init__(self, game, args):
		# game params
		self.board_x, self.board_y = game.getBoardSize()
		self.action_size = game.getActionSize()
		self.args = args

		super(HalfchessNNet, self).__init__()

		self.conv1 = nn.Conv2d(10, args.num_channels, 3, stride=1, padding=1)
		self.bn1 = nn.BatchNorm2d(args.num_channels)

		self.res1 = ResidualBlock(args.num_channels)
		self.se1 = SExBlock(args.num_channels, 16)
		self.res2 = ResidualBlock(args.num_channels)
		self.res3 = ResidualBlock(args.num_channels)

		self.fc = nn.Linear(args.num_channels*(self.board_x)*(self.board_y), 696)
		self.fc_bn = nn.BatchNorm1d(696)

		self.pol = nn.Linear(696, self.action_size)
		self.val = nn.Linear(696, 1)

	def forward(self, s):
		# 															s: batch_size x 10 x board_x x board_y
		s = s.view(-1, 10, self.board_x, self.board_y)				# batch_size x 10 x board_x x board_y
		s = F.relu(self.bn1(self.conv1(s)), inplace=True)	
		s = self.res1(s)											# batch_size x num_channels x board_x x board_y
		s = self.res2(s)
		s = self.res3(s)												# batch_size x num_channels x board_x x board_y
		
		# now flatten it out
		s = s.view(-1, self.args.num_channels*self.board_x*self.board_y)
		s = F.dropout(F.relu(self.fc_bn(self.fc(s))), p=self.args.dropout, training=self.training)	# batch_size x 696

		pi = self.pol(s)	# batch_size * action size
		v = self.val(s)		# batch_size * 1

		return F.log_softmax(pi, dim=1), torch.tanh(v)
