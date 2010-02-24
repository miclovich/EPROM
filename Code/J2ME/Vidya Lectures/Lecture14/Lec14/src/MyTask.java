import java.util.*;


  /**
     *  MyTask - Thread responsible of cyclic processing while the MIDlet is active. 
     */
    class MyTask extends TimerTask {
	// Constructor.
	public MyTask() {
	}
	// .....
	// Thread run method.
	public void run() {
	    System.out.println("Do something sensible here!");
	}
    }
