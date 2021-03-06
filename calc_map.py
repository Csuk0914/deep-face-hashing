import numpy as np

def calc_map(matches, rankings, top_k):
    '''
    Calculate the mean average precision for each of the T test samples, from G
    training/gallery samples.

    Args:
        - matches (numpy.ndarray): a ground-truth matrix mapping whether a
            pair of gallery data and test data are of the same person.
            Shape (G, T).
        - rankings (numpy.ndarray): a sorted index of hamming distance ranking.
            Shape (G, T).
        - top_k (int): the number of shortest distance gallery images to
            compare to the test images.

    Returns:
        (numpy.ndarray): an array containing mean average precision scores for
            each of the T test samples. Of shape (T, )
    '''
    num_gallery, num_test = rankings.shape

    # if top_k is greater than the number of training images, set it to the
    # number of training images, only for testing.
    if num_gallery < top_k: top_k = num_gallery

    correct_retrievals = np.zeros((top_k, num_test), dtype="int8")

    for idx in range(num_test):
        # get the top_k matches for the test data
        rank_slice = rankings[:top_k, idx]
        correct_retrievals[:, idx] = matches[rank_slice, idx]

    # [[1,2,3,...,top_k], [1,2,3,...,top_k]]
    # to facilitate calculating the average precision
    idx = np.linspace(1, top_k, top_k, dtype="int").reshape((top_k, 1))
    correct_idx = np.repeat(idx, num_test, axis=1)
    # sum up all of the scores across the top_k for each test sample
    summed_scores = np.zeros_like(correct_idx)
    for idx in range(top_k):
        # sum the number of correct retrievals from 1 up to idx
        summed_scores[idx, :] = correct_retrievals[:idx+1, :].sum(axis=0)

    # mask out the scores for the incorrect retrievals
    summed_scores = summed_scores * correct_retrievals
    # count the number of correct retrievals to be divided
    num_corrects = correct_retrievals.sum(axis=0)

    # calculate mean average precision
    ap = (summed_scores / correct_idx).sum(axis=0) / num_corrects
    # set the nan values to 0
    ap[ap != ap] = 0

    return ap.mean()

if __name__ == "__main__":
    matches = np.array([
        [1,1,0,1,0],
        [1,0,1,0,1],
        [1,1,1,1,0],
        [0,0,0,0,0],
        [0,0,1,0,1]
    ], dtype="int8")
    ranking = np.array([
        [0,3,2,1,0],
        [4,0,4,0,2],
        [1,4,1,2,3],
        [3,1,0,3,1],
        [2,2,3,4,4]
    ], dtype="int8")
    mean_ap = calc_map(matches, ranking, top_k=3)
    target = np.array([5/6, 1/2, 1, 7/12, 0]).mean()
    assert np.isclose(mean_ap, target), "Invalid calculation!"
