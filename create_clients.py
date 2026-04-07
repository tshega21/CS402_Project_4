from client_utils.client import *
import numpy as np
from data_utils.dataset import data_shuffle
from typing import Union


def get_iid_data(client_id: int, data: tuple[np.ndarray, np.ndarray], total_clients: int, np_rng, **_) -> tuple[np.ndarray, np.ndarray]:
    X_train, y_train = data
    num_per = len(X_train)//total_clients
    # last client receives rest
    if client_id < total_clients - 1:
        data_i = (X_train[client_id*num_per:(client_id+1)*num_per],
                  y_train[client_id*num_per:(client_id+1)*num_per])
    else:
        data_i = (X_train[client_id*num_per:], y_train[client_id*num_per:])
    return data_shuffle(data_i, np_rng)


def distribute_labels(client_id: int, x_train: np.ndarray, y_train: np.ndarray, non_iid_labels: list, total_clients: int, non_iid_method: int):
    num_non_iid_labels = len(non_iid_labels)
    clients_per_noniid_label = total_clients//num_non_iid_labels
    remainder_clients = 0

    if total_clients % num_non_iid_labels != 0:
        remainder_clients = False, total_clients % num_non_iid_labels
        print(
            f"Note that {total_clients} cannot be evenly divided among first {num_non_iid_labels} labels \
            for noniid distribution method {non_iid_method} and label {non_iid_labels[-1]} \
            will be distributed to {remainder_clients} more clients than \
            labels {non_iid_labels[:-1]}")

    label_one = non_iid_labels[
        min(client_id//clients_per_noniid_label, num_non_iid_labels-1)]

    X_label_data, y_label_data = x_train[y_train ==
                                         label_one], y_train[y_train == label_one]

    # remainder clients only apply to last label
    if label_one != non_iid_labels[-1]:
        remainder_clients = 0
    label_amount = len(
        X_label_data)//(clients_per_noniid_label+remainder_clients)
    label_section = client_id % (clients_per_noniid_label + remainder_clients)

    # last label section should be rest of label data
    if label_section < clients_per_noniid_label + remainder_clients - 1:
        X_label_data, y_label_data = X_label_data[label_section*label_amount:(
            label_section+1)*label_amount], y_label_data[label_section*label_amount:(label_section+1)*label_amount]
    else:
        X_label_data, y_label_data = X_label_data[label_section *
                                                  label_amount:], y_label_data[label_section*label_amount:]
    return X_label_data, y_label_data


def get_non_iid_data(i: int, data: tuple[np.ndarray, np.ndarray], total_clients: int, non_iid_method: int, np_rng: np.random.Generator, **_) -> tuple[np.ndarray, np.ndarray]:
    """get appropriate data from x_train, y_train that should be distributed to client i given non_iid_method

    Args:
        i (int):                                client index
        data (tuple[np.ndarray, np.ndarray]):   all training data
        total_clients (int):                    total number of clients
        num_buckets (int):                      number of client buckets
        non_iid_method (int):                   how to distribute data
                                                    method 0:   everyone gets 2 classes 
                                                                1 from first half of labels and 1 from second half or
                                                    method 1:   everyone gets 1 class from first half of labels plus 
                                                                iid distribution of second half of labels
                                                    method 2:   dirchlict

    Returns:
        tuple[np.ndarray, np.ndarray]: subset of x_train and corresponding y_train to distribute to client i
    """
    x_train, y_train = data
    labels = np.unique(y_train)

    if non_iid_method < 2:
        # method 0 and method 1 distribute first half of the labels among the participants

        x_label_data, y_label_data = distribute_labels(
            client_id=i, x_train=x_train, y_train=y_train,
            non_iid_labels=labels[:len(labels)//2],
            total_clients=total_clients, non_iid_method=non_iid_method
        )

        # method 0: everyone gets two classes
        if non_iid_method == 0:

            x_label2_data, y_label2_data = distribute_labels(
                client_id=i, x_train=x_train, y_train=y_train,
                non_iid_labels=labels[len(labels)//2:],
                total_clients=total_clients, non_iid_method=non_iid_method
            )

            client_X_data = np.vstack([x_label_data, x_label2_data])
            client_y_data = np.concatenate([y_label_data, y_label2_data])
            client_data = data_shuffle((client_X_data, client_y_data), np_rng)
            return client_data

        # method 1: everyone get 1 class from first half of the labels and some extra of the second half
        if non_iid_method == 1:
            x_iid_data, y_iid_data = x_train[y_train >=
                                             len(labels)//2], y_train[y_train >= len(labels)//2]

            x_iid_data, y_iid_data = get_iid_data(
                client_id=i, data=(x_iid_data, y_iid_data),
                total_clients=total_clients, np_rng=np_rng
            )

            client_X_data = np.vstack([x_label_data, x_iid_data])
            client_y_data = np.concatenate([y_label_data, y_iid_data])
            client_data = data_shuffle((client_X_data, client_y_data), np_rng)
            return client_data
    # dirchlict, NOTE: alpha is being hard coded at 0.1 here
    if non_iid_method == 2:
        return None
    print(
        f"non_iid_method of {non_iid_method} is not recognized. Expected 0, 1, or 2. Using iid method.")
    return get_iid_data(client_id=i, data=data, total_clients=total_clients, np_rng=np_rng)


def set_dirchlict_distribution(data: tuple[np.ndarray, np.ndarray], batch_size: int, total_clients: int, np_rng: np.random.Generator, **_):
    _, y_train = data

    min_size, alpha = 0, 0.1
    num_labels, num_samples = len(np.unique(y_train)), len(y_train)

    while min_size < batch_size:
        idx_batch = [[] for _ in range(total_clients)]
        for label_num in range(num_labels):
            idx_k = np.where(y_train == label_num)[0]
            np_rng.shuffle(idx_k)
            proportions = np_rng.dirichlet(
                np.repeat(alpha, total_clients))
            proportions = np.array(
                [p*(len(idx_j) < num_samples/total_clients) for p, idx_j in zip(proportions, idx_batch)])
            proportions = proportions/proportions.sum()
            proportions = (np.cumsum(proportions) *
                           len(idx_k)).astype(int)[:-1]
            idx_batch = [idx_j + idx.tolist() for idx_j,
                         idx in zip(idx_batch, np.split(idx_k, proportions))]
            min_size = min([len(idx_j) for idx_j in idx_batch])

    return idx_batch


def get_data(i: int, data: tuple[np.ndarray, np.ndarray], dataset_name: str, accountant_params: dict, np_rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """_summary_

    Args:
        i (int): client index
        data (tuple[np.ndarray, np.ndarray]): full training dataset
        dataset_name (str): dataset name
        accountant_params (dict): dictionary of relevant parameters

    Returns:
        tuple[np.ndarray, np.ndarray]: training data for client i
    """
    if "non_iid" in dataset_name:
        client_data = get_non_iid_data(
            i, data, np_rng=np_rng, **accountant_params)
        if client_data is not None:
            return client_data
        # only return None under dirchlict distribution
        # if distribution is not set in the accountant_params dict, create it
        # NOTE: accountant_params is probably not the best place for this...
        if "dirchlict_distribution" not in accountant_params.keys() or \
                accountant_params["dirchlict_distribution"] is None:
            accountant_params["dirchlict_distribution"] = set_dirchlict_distribution(
                data, np_rng=np_rng, **accountant_params)
        # get client i data given pre-set distribution
        idx_map = accountant_params["dirchlict_distribution"]
        x_train, y_train = data
        return (x_train[idx_map[i]], y_train[idx_map[i]])
    return get_iid_data(i, data, np_rng=np_rng, **accountant_params)


def put_clients_in_buckets(client_lst: list[Client], total_clients: int, num_buckets: int, **_) -> list[list[Client]]:
    num_per_bucket = total_clients//num_buckets
    bucket_lst = [client_lst[i*num_per_bucket:(i*num_per_bucket)+num_per_bucket]
                  for i in range(num_buckets)]
    return bucket_lst


def create_client_lst(data, eps_lst, np_rng: np.random.Generator, accountant_params, my_model, client_opt, client_opt_params, client_model_params, client_fit_params,
                      lr_scheduler, lr_schedule_params, sampling_app, clip_scheduler, dataset_name):

    sampling_lst = generate_sampling_lst(
        sampling_app, np_rng, **accountant_params)

    data_lst = [get_data(i=i, data=data, dataset_name=dataset_name,
                         accountant_params=accountant_params, np_rng=np_rng)
                for i in range(accountant_params['total_clients'])]
    if accountant_params['sort_eps_lst']:
        data_lst.sort(key=lambda x: np.mean(x[1]))

    client_lst = [Client(data=data_lst[i], eps=eps_lst[i], sampling_rate=sampling_lst[i],
                         accountant_params=accountant_params, model_architecture=my_model,
                         np_rng=np_rng, opt=client_opt, opt_params=client_opt_params,
                         model_params=client_model_params, fit_params=client_fit_params,
                         lr_scheduler=lr_scheduler, lr_schedule_params=lr_schedule_params,
                         clip_scheduler=clip_scheduler)
                  for i in range(accountant_params['total_clients'])]
    bucket_lst = put_clients_in_buckets(client_lst, **accountant_params)
    return bucket_lst


def generate_sampling_lst(
        sampling_app: str, np_rng: np.random.Generator,
        total_clients: int, clients_per_round: int,
        min_selection: Union[int, float], num_buckets: int, bucket_prob: list[float],
        **_) -> list[float]:
    # pre - condition: eps_lst must be in order
    if sampling_app == 'uniform':
        return [clients_per_round/total_clients] * total_clients
    if sampling_app == 'normal':
        sampling_lst = np_rng.normal(
            loc=clients_per_round/total_clients, scale=.5*clients_per_round/total_clients, size=total_clients)
        sampling_lst.sort()
        sampling_lst[sampling_lst < min_selection] = min_selection
        sampling_lst[sampling_lst > 1] = 1
        return sampling_lst
    if sampling_app in ['tiered', 'bucket']:
        # Note: this is a little off... technically may need to pass buckets?
        bucket_size = total_clients//num_buckets
        sampling_lst = []
        for i in range(num_buckets-1):
            sampling_lst += bucket_size * \
                [bucket_prob[i] * min(1., clients_per_round/bucket_size)]
        last_bucket_size = total_clients-len(sampling_lst)
        sampling_lst += last_bucket_size * \
            [bucket_prob[-1]*min(1., clients_per_round/last_bucket_size)]
        return sampling_lst
    else:
        # defualt
        return [1.] * total_clients
