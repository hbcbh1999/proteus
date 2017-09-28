from proteus import *
from proteus.default_n import *
from ncls_p import *
from twoD_advection import *
nd = 2

multilevelNonlinearSolver  = Newton
if STABILIZATION_TYPE==0: #SUPG
    levelNonlinearSolver = Newton
    fullNewtonFlag = True
    updateJacobian = True
    timeIntegration = BackwardEuler_cfl
else:
    fullNewtonFlag = False
    updateJacobian = False
    timeIntegration = NCLS.RKEV # SSP33 
    if LUMPED_MASS_MATRIX==True: 
        levelNonlinearSolver = ExplicitLumpedMassMatrix
    else:
        levelNonlinearSolver = ExplicitConsistentMassMatrixWithRedistancing

stepController = Min_dt_controller
timeOrder = SSPOrder
nStagesTime = SSPOrder

if useHex:
    quad=True
    if pDegree_ncls == 1:
        femSpaces = {0:C0_AffineLinearOnCubeWithNodalBasis}
    elif pDegree_ncls == 2:
        if useBernstein:
            femSpaces = {0:C0_AffineBernsteinOnCube}
        else:
            femSpaces = {0:C0_AffineLagrangeOnCubeWithNodalBasis}
    else:
        print "pDegree = %s not recognized " % pDegree_ncls
    elementQuadrature = CubeGaussQuadrature(nd,twoD_advection_quad_order)
    elementBoundaryQuadrature = CubeGaussQuadrature(nd-1,twoD_advection_quad_order)
else:
    if pDegree_ncls == 1:
        femSpaces = {0:C0_AffineLinearOnSimplexWithNodalBasis}
    elif pDegree_ncls == 2:
        femSpaces = {0:C0_AffineQuadraticOnSimplexWithNodalBasis}
    else:
        print "pDegree = %s not recognized " % pDegree_ncls
    elementQuadrature = SimplexGaussQuadrature(nd,twoD_advection_quad_order)
    elementBoundaryQuadrature = SimplexGaussQuadrature(nd-1,twoD_advection_quad_order)

nonlinearSmoother = None
subgridError = None
#subgridError = HamiltonJacobi_ASGS_opt(coefficients,nd,lag=True)

#numericalFluxType = NCLS.NumericalFlux
#numericalFluxType = DoNothing
numericalFluxType = Advection_DiagonalUpwind_IIPG_exterior # PERIODIC

shockCapturing = NCLS.ShockCapturing(coefficients,nd,shockCapturingFactor=shockCapturingFactor_ncls,lag=lag_shockCapturing_ncls)

tolFac = 0.0

nl_atol_res = atolLevelSet
l_atol_res = atolLevelSet

maxNonlinearIts = 20
maxLineSearches = 0

matrix = SparseMatrix

if parallel:
    multilevelLinearSolver = KSP_petsc4py#PETSc
    levelLinearSolver = KSP_petsc4py#PETSc
    linear_solver_options_prefix = 'ncls_'
    linearSolverConvergenceTest = 'r-true'
else:
    multilevelLinearSolver = LU    
    levelLinearSolver = LU

conservativeFlux = {}
if checkMass:
    auxiliaryVariables = [MassOverRegion()]

tnList=[0.,1E-6]+[float(n)*T/float(nDTout) for n in range(1,nDTout+1)]