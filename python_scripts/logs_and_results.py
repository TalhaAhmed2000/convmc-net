import datetime
import os
import time
import matplotlib.pyplot as plt
import numpy as np

ROOT = '/home/gcf/Desktop/Talha_Nehal Sproj/Tahir Sproj Stuff/SPROJ_ConvMC_Net/Sensor_Data'

# Small Helper Function to modularize training loop
# Short functions to get sampling rate and noise variables as strings. make_dir is a function which takes the appropriate noise and sampling rate directory and makes there a directory for either logs or
# saved models or plots (for both convmc and admm). get_modularized_record() takes the project name, hyperparameters, q and sigma and returns its file path either that be a log file or a title for a plot
def get_q_str(q):
  q_exp = f'{q * 100}%'
  return q_exp

def get_noise_str(sigma):
  noise_exp = f'{float(sigma)}'
  return noise_exp

def make_dir(q, sigma, new_entry, hyper_param_net):
  new_dir = ROOT + '/Q is ' + get_q_str(q) + '/Noise Variance ' + get_noise_str(sigma) + '/' + new_entry
  os.makedirs(new_dir, exist_ok = True)

  convmc_dir = new_dir + '/ConvMC-Net'
  os.makedirs(convmc_dir, exist_ok = True)

  admm_dir = new_dir + '/ADMM-Net'
  os.makedirs(admm_dir, exist_ok = True)

  if hyper_param_net['Model'] == 'ADMM-Net':
    return admm_dir
  else:
    return convmc_dir

# Making a small function which makes directories for different tries for different models
def make_session(q, sigma, new_entry, hyper_param_net, session_no):
  # Get dir of activity/record to make sessions of
  dir = make_dir(q, sigma, new_entry, hyper_param_net)

  # Now make a session corresponding to whichever try is going on currently
  session_dir = dir + '/' + session_no
  os.makedirs(session_dir, exist_ok = True)

  return session_dir

# Making a small function to get date and time according to our time zone. Will be used to create the logs
def get_current_time():
  ts = time.time()
  st = datetime.datetime.fromtimestamp(ts)

  # Add 5 hours to the datetime according to our time zone
  new_time = st + datetime.timedelta(hours = 5)

  formatted_new_time = new_time.strftime('%Y-%m-%d %H:%M:%S')

  return formatted_new_time

def make_predictions_dir(project_name, q, sigma, new_entry, params_net, hyper_param_net, SESSION):
  # Get Directory with ADMM-Net/ConvMC-Net --> Session directories built
  dir = make_session(q, sigma, new_entry, hyper_param_net, SESSION)

  # Make a children directory after Session --> ProjectName + parameters --> Train/Test which will contain the final predictions on our train and test data used to evaluate the model after training phase
  param_project_dir = (f'{dir}/{project_name} Layers_{params_net["layers"]}_Alpha_{hyper_param_net["Alpha"]:.2f}_TrainInstances_{hyper_param_net["TrainInstances"]}_Epochs_{hyper_param_net["Epochs"]}_lr_{hyper_param_net["Lr"]}')
  os.makedirs(param_project_dir, exist_ok = True)

  # Train/Test Dir dir
  train_dir = param_project_dir + '/train'
  test_dir = param_project_dir + '/test'

  os.makedirs(train_dir, exist_ok = True)
  os.makedirs(test_dir, exist_ok = True)

  # Return Train and Test Directories to store data in
  return train_dir, test_dir

def get_modularized_record(project_name, q, sigma, new_entry, hyper_param_net, params_net, SESSION, current_epoch = None):

  # Get directory
  dir = make_session(q, sigma, new_entry, hyper_param_net, SESSION)
  if current_epoch == None:
    log_path = (f'{dir}/{project_name} Layers_{params_net["layers"]}_Alpha_{hyper_param_net["Alpha"]:.2f}_TrainInstances_{hyper_param_net["TrainInstances"]}_Epochs_{hyper_param_net["Epochs"]}_lr_{hyper_param_net["Lr"]}.txt')
    return log_path
  elif new_entry == 'Plots':
    model_path = (f'{dir}/{project_name} Layers_{params_net["layers"]}_Alpha_{hyper_param_net["Alpha"]:.2f}_TrainInstances_{hyper_param_net["TrainInstances"]}_Epochs_[{current_epoch}_out_of_{hyper_param_net["Epochs"]}]_lr_{hyper_param_net["Lr"]}.png')
    return model_path
  else:
    model_path = (f'{dir}/{project_name} Layers_{params_net["layers"]}_Alpha_{hyper_param_net["Alpha"]:.2f}_TrainInstances_{hyper_param_net["TrainInstances"]}_Epochs_[{current_epoch}_out_of_{hyper_param_net["Epochs"]}]_lr_{hyper_param_net["Lr"]}.pth')
    return model_path

def plot_and_save_mse_vs_epoch(training_loss, validation_loss, dir):
  # Data extracted from the input
    epochs = list(range(1, len(training_loss) + 1))

    # Creating plots with updated legend descriptions
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    # Plot training loss with updated legend
    axs[0].plot(epochs, training_loss, 'bo-', label=r'$loss_{train} = \frac{\|M - X\|{2}^2}{\|X\|{F}^2}$')
    axs[0].set_title('Training Loss per Epoch')
    axs[0].set_xlabel('Epoch')
    axs[0].set_ylabel('Mean Training Loss')
    axs[0].grid(True)
    axs[0].legend()

    # Plot validation loss with updated legend
    axs[1].plot(epochs, validation_loss, 'r^-', label=r'$loss_{val} = \frac{\|M - X\|_{F}^2}{n_1n_2}$')
    axs[1].set_title('Validation Loss per Epoch')
    axs[1].set_xlabel('Epoch')
    axs[1].set_ylabel('Mean Validation Loss')
    axs[1].grid(True)
    axs[1].legend()

    plt.tight_layout()
    plt.savefig(dir)
    plt.show()
