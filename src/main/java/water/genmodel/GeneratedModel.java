package water.genmodel;

/** This is a helper class to support Java generated models.
 */
public abstract class GeneratedModel implements IGeneratedModel {
  @Override public int      getNumCols()      { return getNames().length - 1; }
  @Override public int      getResponseIdx () { return getNames().length - 1; }
  @Override public String   getResponseName() { return getNames()[getResponseIdx()]; }
  @Override public String[] getDomainValues(int i) { return getDomainValues()[i]; }
  @Override public int      getNumResponseClasses() { return getNumClasses(getResponseIdx()); }

  @Override public int getColIdx(String name) {
    String[] names = getNames();
    for (int i=0; i<names.length; i++) if (names[i].equals(name)) return i;
    return -1;
  }
  @Override public int getNumClasses(int i) {
    String[] domval = getDomainValues(i);
    return domval!=null?domval.length:-1;
  }
  @Override public String[] getDomainValues(String name) {
    int colIdx = getColIdx(name);
    return colIdx != -1 ? getDomainValues(colIdx) : null;
  }

  public static int maxIndex(float[] from, int start) {
    int result = start;
    for (int i = start; i<from.length; ++i)
      if (from[i]>from[result]) result = i;
    return result;
  }
}