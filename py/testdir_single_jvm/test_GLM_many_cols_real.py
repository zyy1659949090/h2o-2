import unittest
import random, sys, time, os, getpass
sys.path.extend(['.','..','py'])
import h2o, h2o_cmd, h2o_hosts, h2o_browse as h2b, h2o_import as h2i, h2o_glm

def write_syn_dataset(csvPathname, rowCount, colCount, SEED):
    # 8 random generatators, 1 per column
    r1 = random.Random(SEED)
    dsf = open(csvPathname, "w+")

    for i in range(rowCount):
        rowData = []
        rowTotal = 0
        # having reals makes it less likely to fail to converge?
        for j in range(colCount):
            ri1 = int(r1.gauss(1,.1))
            rowTotal += ri1
            rowData.append(ri1 + 0.1) # odd bias shift

        # sum the row, and make output 1 if > (5 * rowCount)
        if (rowTotal > (0.5 * colCount)): 
            result = 1
        else:
            result = 0

        rowData.append(result)
        ### print colCount, rowTotal, result
        rowDataCsv = ",".join(map(str,rowData))
        dsf.write(rowDataCsv + "\n")

    dsf.close()


class Basic(unittest.TestCase):
    def tearDown(self):
        h2o.check_sandbox_for_errors()

    @classmethod
    def setUpClass(cls):
        global SEED
        SEED = random.randint(0, sys.maxint)

        # SEED = 
        random.seed(SEED)
        print "\nUsing random seed:", SEED
        localhost = h2o.decide_if_localhost()
        global tryHeap
        tryHeap = 14
        if (localhost):
            h2o.build_cloud(1, enable_benchmark_log=True, java_heap_GB=tryHeap)
        else:
            h2o_hosts.build_cloud_with_hosts(enable_benchmark_log=True)

    @classmethod
    def tearDownClass(cls):
        h2o.tear_down_cloud()

    def test_GLM_many_cols_real(self):
        SYNDATASETS_DIR = h2o.make_syn_dir()
        if getpass.getuser() == 'kevin': # longer run
            tryList = [
                (100, 1000, 'cA', 100),
                (100, 3000, 'cB', 300),
                (100, 5000, 'cC', 1500),
                (100, 7000, 'cD', 3600),
                (100, 9000, 'cE', 3600),
                (100, 10000, 'cF', 3600),
                ]
        else:
            tryList = [
                (100, 1000, 'cA', 100),
                (100, 3000, 'cB', 300),
                ]

        ### h2b.browseTheCloud()
        for (rowCount, colCount, key2, timeoutSecs) in tryList:
            SEEDPERFILE = random.randint(0, sys.maxint)
            csvFilename = 'syn_' + str(SEEDPERFILE) + "_" + str(rowCount) + 'x' + str(colCount) + '.csv'
            csvPathname = SYNDATASETS_DIR + '/' + csvFilename

            print "Creating random", csvPathname
            write_syn_dataset(csvPathname, rowCount, colCount, SEEDPERFILE)

            start = time.time()
            parseKey = h2o_cmd.parseFile(None, csvPathname, key2=key2, timeoutSecs=10)
            elapsed = time.time() - start
            print csvFilename, 'parse time:', parseKey['response']['time']
            print "Parse result['destination_key']:", parseKey['destination_key']

            algo = "Parse"
            l = '{:d} jvms, {:d}GB heap, {:s} {:s} {:6.2f} secs'.format(
                len(h2o.nodes), tryHeap, algo, csvFilename, elapsed)
            print l
            h2o.cloudPerfH2O.message(l)

            # We should be able to see the parse result?
            inspect = h2o_cmd.runInspect(None, parseKey['destination_key'])
            print "\n" + csvFilename

            y = colCount
            # just limit to 2 iterations..assume it scales with more iterations
            kwargs = {
                'y': y,
                'max_iter': 2, 
                'case': 1,
                'case_mode': '=',
                'family': 'binomial',
                'lambda': 1.e-4,
                'alpha': 0.6,
                'weight': 1.0,
                'thresholds': 0.5,
                'n_folds': 1,
                'beta_eps': 1.e-4,
            }

            start = time.time()
            glm = h2o_cmd.runGLMOnly(parseKey=parseKey, timeoutSecs=timeoutSecs, **kwargs)
            elapsed = time.time() - start
            h2o.check_sandbox_for_errors()
            print "glm end on ", csvPathname, 'took', elapsed, 'seconds', \
                "%d pct. of timeout" % ((elapsed*100)/timeoutSecs)
            h2o_glm.simpleCheckGLM(self, glm, None, **kwargs)

            iterations = glm['GLMModel']['iterations']

            algo = "GLM " + str(iterations) + " iterations"
            l = '{:d} jvms, {:d}GB heap, {:s} {:s} {:6.2f} secs'.format(
                len(h2o.nodes), tryHeap, algo, csvFilename, elapsed)
            print l
            h2o.cloudPerfH2O.message(l)

if __name__ == '__main__':
    h2o.unit_main()
