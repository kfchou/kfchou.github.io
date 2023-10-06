---
layout: post
title: Displaying and saving live serial port data with FuncAnimation
categories: [Visualizations, matplotlib, python]
---

<image src="{{ site.baseurl }}/images/raindrops.gif" alt="inspired by Matplotlib's raindrop simulation"/>

The internet has plenty of guides on funcAnimation if you want to:
* Display the evolution of data by defining an equation and create a gif or video from it
  * [Animating a ball bouncing](https://scipython.com/book2/chapter-7-matplotlib/examples/animating-a-bouncing-ball/)
  * [A rolling circle](https://pythonmatplotlibtips.blogspot.com/2017/12/cycloid-animation-funcanimation.html)
  * [Lots more on matplotlib](https://matplotlib.org/stable/gallery/animation/index.html)
* Display the evolution of data by by importing said data from disk
  * [Generate data externally](https://www.youtube.com/watch?v=Ercd-Ip5PfQ)
* Display live data by reading from the serial port using `pyserial`
  * [Reading from an Audrino](http://www.mikeburdis.com/wp/notes/plotting-serial-port-data-using-python-and-matplotlib/)

What if you want to both display the live data from the serial port  ***and*** save the animation? Here are some important concepts that will help answer this question.

Note: I won't discuss how to read live data from the serial port here. There are plenty of good articles on that topic.

# Understanding the basic `FuncAnimation` call
```py
    from matplotlib.animation import FuncAnimation

    ani = FuncAnimation(
        fig=fig, # fig = plt.figure(...)
        init_func=init, # function to set up your canvas, optional
        func=update, # function to update your canvas in fig using the generator data
        frames=generator, # functions to generate the data to be displayed
        interval=interval*1000, # in milliseconds
        save_count=200, # number of frames to save for writing to disk
        blit=False
    )
```

Under the hood:
1. `FuncAnimation` calls the function you provided in `init_func`, this is where you set up your first animation frame.
2. The `generator` function is called. This provides the data to the `update` function. This is usually where you update the lines on your canvas.



# To display live data, save to disk first, then read from disk
Our first instinct is to read the live data from a memory buffer. Reading from disk seems counterintuitive; but it works. I found that this has minimal impact on performance.

To continuously update the live data, keep writing the data to disk. Then, use a generator function to read latest data and feed that data to the `update` function.

The `generator` is called once per `interval`. If your data is updated continuously, then everytime the `generator` is called, then you can read in the latest data from the generator, then display it.


```py
    def generator(lines_written, tail_len) -> pd.DataFrame:
        """
        Generator function to read and yield data from a CSV file.

        Args:
            lines_written: Number of lines already written to disk.
            tail_len: Number of lines you want to display.

        Yields:
            pd.DataFrame: A DataFrame containing the read data.
        """
        # read the last tail_len lines from the file
        if lines_written + 1 < tail_len:
            df = pd.read_csv(file_name)
        else:
            df = pd.read_csv(file_name, skiprows=range(1, lines_written - tail_len))

        yield df

    # create a figure for the animaion
    fig = plt.figure(...)

    # define the animation function
    ani = FuncAnimation(
        fig=fig,
        frames=generator,
        ...
    )

    # execute
    plt.show()
```

`FuncAnimation()` is not actually executed until `plt.show()` is called. If using Jupyter notebook, you can also just call `ani` like in this [example](https://pythonmatplotlibtips.blogspot.com/2017/12/cycloid-animation-funcanimation.html).

# Saving the animation
Unfortunately, this is not as easy as calling `ani.save()`.

If you simply call
```py
    ani = FuncAnimation(
        fig=fig,
        init_func=init, # optional
        func=update, 
        frames=partial(
            generator, 
            lines_written=lines_written, 
            tail_len=tail_len
            ),
        interval=interval*1000, # in milliseconds
        save_count=200, # number of frames to save for writing to disk
        blit=False
    )

    # define the animation function
    writergif = animation.PillowWriter(fps=desired_frame_rate) 
    ani.save(filename=f"my_animation.gif", writer=writergif)

```
Then you'll only see the last frame of the animation. Why? Because `generator` is static as written. It will only read the last `tail_len` lines of your data file, then display it.

Instead, you need to write a *new* generator in a way that provides a series of data, corresponding to each frame of the animation.

Let's say we want to read `tail_len` lines of data for every frame, and display that data. Additionally, we want to increment the lines read by 250 lines per frame. The new generator would look like this:

```py
    def generator_with_complete_data(file_name):
        """Generator for saving animation after data collection has finished.
        
        The data for every frame is created by each `yield` return within the while loop.
        """
        # assuming tail_len is defined somewhere
        df = pd.read_csv(file_name)
        
        frame_num = 0
        lines_per_frame = 250
        line_end = 1250 # first frame size
        while line_end <= df.shape[0]:
            # read a minimum of 1250 lines
            line_end = 1250+lines_per_frame*frame_num
            if line_end < tail_len:
                line_start = 0
            else:
                line_start = line_end - tail_len
            frame_num += 1
            yield df.iloc[line_start:line_end] # yeets the data to the update function.

    # define the animation function
    ani = FuncAnimation(
        fig = fig,
        frames=generator_with_complete_data(file_name=file_name),
        ...
    )

    # execute and save
    writergif = animation.PillowWriter(fps=desired_frame_rate) 
    ani.save(filename=f"my_animation.gif", writer=writergif)
```

In this use case, it is very common to see the `while`/`yield` pattern.

Now, when `ani.save()` is called, `FuncAnimation` is executed. It will call `generator_with_complete_data()`, then for each object yielded in the while loop, write that data object to each frame.

# Summary
To both view the live data ***and*** save that animation, two separate generators must be used. Meaning you must do the following:
1. Write a generator to continuously read the latest data for display.
2. Write a separate generator to read the complete data, but only giving `FuncAnimation` the appropriate data to display in each frame.
3. Have one FuncAnimation call for live data display, executing it with `plt.show()`
4. Have a separate FuncAnimation call for generating the animation for the complete data, executing it with `ani.save()`.

Hopefully you now have a better understanding of generator functions and their interactions with FuncAnimation. Happy coding!

---

Note: *Header image is based on Matplotlib's [raindrop simulation](https://matplotlib.org/stable/gallery/animation/rain.html#sphx-glr-gallery-animation-rain-py).*
