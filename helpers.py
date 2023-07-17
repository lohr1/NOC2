import casadi as ca


def smooth_norm(v):
    """
    Smooths Euclidean norm by adding small epsilon under the sqrt.
    :param v: casadi MX column vector to find smooth norm of
    :return: sqrt(v.T * v + e)
    """
    epsilon = 1e-6
    return ca.sqrt(ca.dot(v, v) + epsilon)
