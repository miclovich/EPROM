import java.util.TimerTask;

public class GameTimer extends TimerTask {

	int timeLeft;

	public GameTimer(int maxTime) {
		timeLeft = maxTime;
	}

	public void run() {
		timeLeft--;
	}

	public int getTimeLeft() { return this.timeLeft; }
}